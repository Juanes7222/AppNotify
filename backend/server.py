from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(
    mongo_url,
    tls=True,
    tlsAllowInvalidCertificates=True
)
db = client[os.environ['DB_NAME']]

# Firebase verification URL
FIREBASE_VERIFY_URL = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo"

# Create the main app
app = FastAPI(title="Event Reminder System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===================== MODELS =====================

class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    photo_url: Optional[str] = None

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firebase_uid: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Contact(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    notes: Optional[str] = None

class ReminderInterval(BaseModel):
    value: int
    unit: str  # 'minutes', 'hours', 'days', 'weeks'

class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: Optional[str] = None
    event_date: datetime
    location: Optional[str] = None
    reminder_intervals: List[ReminderInterval] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: datetime
    location: Optional[str] = None
    reminder_intervals: List[ReminderInterval] = []

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    reminder_intervals: Optional[List[ReminderInterval]] = None

class Subscription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    contact_id: str
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SubscriptionCreate(BaseModel):
    contact_id: str

class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    subscription_id: str
    contact_id: str
    user_id: str
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, failed
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DashboardStats(BaseModel):
    total_events: int
    upcoming_events: int
    total_contacts: int
    pending_notifications: int
    sent_notifications: int

# ===================== AUTH =====================

async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="No authentication token provided")
    
    token = credentials.credentials
    firebase_api_key = os.environ.get('FIREBASE_API_KEY', '')
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FIREBASE_VERIFY_URL}?key={firebase_api_key}",
                json={"idToken": token}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid authentication token")
            
            data = response.json()
            if "users" not in data or len(data["users"]) == 0:
                raise HTTPException(status_code=401, detail="User not found")
            
            user_info = data["users"][0]
            return {
                "uid": user_info.get("localId"),
                "email": user_info.get("email"),
                "display_name": user_info.get("displayName"),
                "photo_url": user_info.get("photoUrl")
            }
    except httpx.RequestError:
        raise HTTPException(status_code=401, detail="Failed to verify token")

async def get_or_create_user(user_info: dict) -> dict:
    existing_user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    
    if existing_user:
        return existing_user
    
    new_user = User(
        firebase_uid=user_info["uid"],
        email=user_info["email"],
        display_name=user_info.get("display_name"),
        photo_url=user_info.get("photo_url")
    )
    
    user_dict = new_user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    
    await db.users.insert_one(user_dict)
    return new_user.model_dump()

# ===================== ROUTES =====================

@api_router.get("/")
async def root():
    return {"message": "Event Reminder System API"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

# Auth routes
@api_router.post("/auth/verify")
async def verify_token(user_info: dict = Depends(verify_firebase_token)):
    user = await get_or_create_user(user_info)
    return {"user": user, "message": "Authentication successful"}

@api_router.get("/auth/me")
async def get_current_user(user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Dashboard routes
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = user["id"]
    now = datetime.now(timezone.utc)
    
    total_events = await db.events.count_documents({"user_id": user_id})
    upcoming_events = await db.events.count_documents({
        "user_id": user_id,
        "event_date": {"$gte": now.isoformat()}
    })
    total_contacts = await db.contacts.count_documents({"user_id": user_id})
    pending_notifications = await db.notifications.count_documents({
        "user_id": user_id,
        "status": "pending"
    })
    sent_notifications = await db.notifications.count_documents({
        "user_id": user_id,
        "status": "sent"
    })
    
    return DashboardStats(
        total_events=total_events,
        upcoming_events=upcoming_events,
        total_contacts=total_contacts,
        pending_notifications=pending_notifications,
        sent_notifications=sent_notifications
    )

@api_router.get("/dashboard/next-event")
async def get_next_event(user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    now = datetime.now(timezone.utc)
    event = await db.events.find_one(
        {"user_id": user["id"], "event_date": {"$gte": now.isoformat()}},
        {"_id": 0},
        sort=[("event_date", 1)]
    )
    
    if event:
        subscribers_count = await db.subscriptions.count_documents({"event_id": event["id"]})
        event["subscribers_count"] = subscribers_count
    
    return event

@api_router.get("/dashboard/recent-activity")
async def get_recent_activity(user_info: dict = Depends(verify_firebase_token), limit: int = 10):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notifications = await db.notifications.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Enrich with event and contact info
    enriched = []
    for notif in notifications:
        event = await db.events.find_one({"id": notif["event_id"]}, {"_id": 0})
        contact = await db.contacts.find_one({"id": notif["contact_id"]}, {"_id": 0})
        enriched.append({
            **notif,
            "event_title": event["title"] if event else "Unknown Event",
            "contact_name": contact["name"] if contact else "Unknown Contact",
            "contact_email": contact["email"] if contact else ""
        })
    
    return enriched

# Contact routes
@api_router.get("/contacts", response_model=List[dict])
async def get_contacts(user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    contacts = await db.contacts.find({"user_id": user["id"]}, {"_id": 0}).to_list(1000)
    return contacts

@api_router.post("/contacts", response_model=dict)
async def create_contact(contact_data: ContactCreate, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    contact = Contact(
        user_id=user["id"],
        **contact_data.model_dump()
    )
    
    contact_dict = contact.model_dump()
    contact_dict['created_at'] = contact_dict['created_at'].isoformat()
    
    await db.contacts.insert_one(contact_dict)
    return contact_dict

@api_router.get("/contacts/{contact_id}", response_model=dict)
async def get_contact(contact_id: str, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    contact = await db.contacts.find_one({"id": contact_id, "user_id": user["id"]}, {"_id": 0})
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact

@api_router.put("/contacts/{contact_id}", response_model=dict)
async def update_contact(contact_id: str, contact_data: ContactCreate, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    contact = await db.contacts.find_one({"id": contact_id, "user_id": user["id"]}, {"_id": 0})
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    update_data = contact_data.model_dump()
    await db.contacts.update_one({"id": contact_id}, {"$set": update_data})
    
    updated_contact = await db.contacts.find_one({"id": contact_id}, {"_id": 0})
    return updated_contact

@api_router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await db.contacts.delete_one({"id": contact_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Delete related subscriptions and notifications
    await db.subscriptions.delete_many({"contact_id": contact_id})
    await db.notifications.delete_many({"contact_id": contact_id})
    
    return {"message": "Contact deleted successfully"}

# Event routes
@api_router.get("/events", response_model=List[dict])
async def get_events(user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    events = await db.events.find({"user_id": user["id"]}, {"_id": 0}).sort("event_date", 1).to_list(1000)
    
    # Add subscriber count to each event
    for event in events:
        event["subscribers_count"] = await db.subscriptions.count_documents({"event_id": event["id"]})
    
    return events

@api_router.post("/events", response_model=dict)
async def create_event(event_data: EventCreate, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    event = Event(
        user_id=user["id"],
        **event_data.model_dump()
    )
    
    event_dict = event.model_dump()
    event_dict['event_date'] = event_dict['event_date'].isoformat()
    event_dict['created_at'] = event_dict['created_at'].isoformat()
    event_dict['updated_at'] = event_dict['updated_at'].isoformat()
    
    await db.events.insert_one(event_dict)
    event_dict["subscribers_count"] = 0
    return event_dict

@api_router.get("/events/{event_id}", response_model=dict)
async def get_event(event_id: str, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    event = await db.events.find_one({"id": event_id, "user_id": user["id"]}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event["subscribers_count"] = await db.subscriptions.count_documents({"event_id": event_id})
    return event

@api_router.put("/events/{event_id}", response_model=dict)
async def update_event(event_id: str, event_data: EventUpdate, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    event = await db.events.find_one({"id": event_id, "user_id": user["id"]}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = {k: v for k, v in event_data.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    if 'event_date' in update_data:
        update_data['event_date'] = update_data['event_date'].isoformat()
        # Regenerate notifications if date changed
        await regenerate_notifications(event_id, user["id"])
    
    await db.events.update_one({"id": event_id}, {"$set": update_data})
    
    updated_event = await db.events.find_one({"id": event_id}, {"_id": 0})
    updated_event["subscribers_count"] = await db.subscriptions.count_documents({"event_id": event_id})
    return updated_event

@api_router.delete("/events/{event_id}")
async def delete_event(event_id: str, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await db.events.delete_one({"id": event_id, "user_id": user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Delete related subscriptions and notifications
    await db.subscriptions.delete_many({"event_id": event_id})
    await db.notifications.delete_many({"event_id": event_id})
    
    return {"message": "Event deleted successfully"}

# Subscription routes
@api_router.get("/events/{event_id}/subscriptions", response_model=List[dict])
async def get_event_subscriptions(event_id: str, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    event = await db.events.find_one({"id": event_id, "user_id": user["id"]}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    subscriptions = await db.subscriptions.find({"event_id": event_id}, {"_id": 0}).to_list(1000)
    
    # Enrich with contact info
    enriched = []
    for sub in subscriptions:
        contact = await db.contacts.find_one({"id": sub["contact_id"]}, {"_id": 0})
        if contact:
            enriched.append({**sub, "contact": contact})
    
    return enriched

@api_router.post("/events/{event_id}/subscriptions", response_model=dict)
async def add_subscription(event_id: str, sub_data: SubscriptionCreate, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    event = await db.events.find_one({"id": event_id, "user_id": user["id"]}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    contact = await db.contacts.find_one({"id": sub_data.contact_id, "user_id": user["id"]}, {"_id": 0})
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Check if subscription already exists
    existing = await db.subscriptions.find_one({
        "event_id": event_id,
        "contact_id": sub_data.contact_id
    }, {"_id": 0})
    
    if existing:
        raise HTTPException(status_code=400, detail="Contact already subscribed to this event")
    
    subscription = Subscription(
        event_id=event_id,
        contact_id=sub_data.contact_id,
        user_id=user["id"]
    )
    
    sub_dict = subscription.model_dump()
    sub_dict['created_at'] = sub_dict['created_at'].isoformat()
    
    await db.subscriptions.insert_one(sub_dict)
    
    # Generate notifications for this subscription
    await generate_notifications_for_subscription(event, subscription, user["id"])
    
    return {**sub_dict, "contact": contact}

@api_router.delete("/events/{event_id}/subscriptions/{subscription_id}")
async def remove_subscription(event_id: str, subscription_id: str, user_info: dict = Depends(verify_firebase_token)):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await db.subscriptions.delete_one({
        "id": subscription_id,
        "event_id": event_id,
        "user_id": user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Delete related notifications
    await db.notifications.delete_many({"subscription_id": subscription_id})
    
    return {"message": "Subscription removed successfully"}

# Notification routes
@api_router.get("/notifications", response_model=List[dict])
async def get_notifications(
    user_info: dict = Depends(verify_firebase_token),
    status: Optional[str] = None,
    limit: int = 100
):
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = {"user_id": user["id"]}
    if status:
        query["status"] = status
    
    notifications = await db.notifications.find(query, {"_id": 0}).sort("scheduled_at", -1).to_list(limit)
    
    # Enrich with event and contact info
    enriched = []
    for notif in notifications:
        event = await db.events.find_one({"id": notif["event_id"]}, {"_id": 0})
        contact = await db.contacts.find_one({"id": notif["contact_id"]}, {"_id": 0})
        enriched.append({
            **notif,
            "event_title": event["title"] if event else "Unknown Event",
            "event_date": event["event_date"] if event else None,
            "contact_name": contact["name"] if contact else "Unknown Contact",
            "contact_email": contact["email"] if contact else ""
        })
    
    return enriched

# ===================== HELPER FUNCTIONS =====================

def calculate_notification_time(event_date: datetime, interval: ReminderInterval) -> datetime:
    """Calculate when a notification should be sent based on event date and interval"""
    if isinstance(event_date, str):
        event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
    
    if interval.unit == 'minutes':
        return event_date - timedelta(minutes=interval.value)
    elif interval.unit == 'hours':
        return event_date - timedelta(hours=interval.value)
    elif interval.unit == 'days':
        return event_date - timedelta(days=interval.value)
    elif interval.unit == 'weeks':
        return event_date - timedelta(weeks=interval.value)
    return event_date

async def generate_notifications_for_subscription(event: dict, subscription: Subscription, user_id: str):
    """Generate notification documents for a new subscription"""
    event_date = event['event_date']
    if isinstance(event_date, str):
        event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
    
    for interval in event.get('reminder_intervals', []):
        interval_obj = ReminderInterval(**interval) if isinstance(interval, dict) else interval
        scheduled_at = calculate_notification_time(event_date, interval_obj)
        
        # Only create notification if it's in the future
        if scheduled_at > datetime.now(timezone.utc):
            notification = Notification(
                event_id=event['id'],
                subscription_id=subscription.id,
                contact_id=subscription.contact_id,
                user_id=user_id,
                scheduled_at=scheduled_at
            )
            
            notif_dict = notification.model_dump()
            notif_dict['scheduled_at'] = notif_dict['scheduled_at'].isoformat()
            notif_dict['created_at'] = notif_dict['created_at'].isoformat()
            
            await db.notifications.insert_one(notif_dict)

async def regenerate_notifications(event_id: str, user_id: str):
    """Regenerate all notifications for an event (when event date changes)"""
    # Delete pending notifications
    await db.notifications.delete_many({
        "event_id": event_id,
        "status": "pending"
    })
    
    event = await db.events.find_one({"id": event_id}, {"_id": 0})
    if not event:
        return
    
    subscriptions = await db.subscriptions.find({"event_id": event_id}, {"_id": 0}).to_list(1000)
    
    for sub in subscriptions:
        subscription = Subscription(**sub)
        await generate_notifications_for_subscription(event, subscription, user_id)

# ===================== EMAIL SCHEDULER =====================

async def send_email(to_email: str, subject: str, body: str):
    """Send email via Gmail SMTP"""
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    
    if not smtp_user or not smtp_password:
        logger.warning("SMTP credentials not configured, skipping email send")
        return False
    
    message = MIMEMultipart()
    message['From'] = smtp_user
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'html'))
    
    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

async def process_pending_notifications():
    """Process and send pending notifications"""
    try:
        now = datetime.now(timezone.utc)
        
        pending = await db.notifications.find({
            "status": "pending",
            "scheduled_at": {"$lte": now.isoformat()}
        }, {"_id": 0}).to_list(100)
    except Exception as e:
        logger.error(f"Error fetching pending notifications: {e}")
        return
    
    for notif in pending:
        try:
            # Get event and contact info
            event = await db.events.find_one({"id": notif["event_id"]}, {"_id": 0})
            contact = await db.contacts.find_one({"id": notif["contact_id"]}, {"_id": 0})
            
            if not event or not contact:
                await db.notifications.update_one(
                    {"id": notif["id"]},
                    {"$set": {"status": "failed", "error_message": "Event or contact not found"}}
                )
                continue
            
            # Parse event date
            event_date = event['event_date']
            if isinstance(event_date, str):
                event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
            
            # Build email content
            subject = f"Recordatorio: {event['title']}"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #6366F1;">Recordatorio de Evento</h2>
                <p>Hola <strong>{contact['name']}</strong>,</p>
                <p>Este es un recordatorio para el siguiente evento:</p>
                <div style="background: #f4f4f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #09090B;">{event['title']}</h3>
                    <p style="margin: 5px 0;"><strong>Fecha:</strong> {event_date.strftime('%d/%m/%Y %H:%M')}</p>
                    {f"<p style='margin: 5px 0;'><strong>Ubicación:</strong> {event['location']}</p>" if event.get('location') else ""}
                    {f"<p style='margin: 5px 0;'><strong>Descripción:</strong> {event['description']}</p>" if event.get('description') else ""}
                </div>
                <p style="color: #71717A; font-size: 12px;">Este es un mensaje automático del sistema de recordatorios.</p>
            </body>
            </html>
            """
            
            # Send email
            success = await send_email(contact['email'], subject, body)
            
            if success:
                await db.notifications.update_one(
                    {"id": notif["id"]},
                    {"$set": {
                        "status": "sent",
                        "sent_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                logger.info(f"Notification sent to {contact['email']} for event {event['title']}")
            else:
                await db.notifications.update_one(
                    {"id": notif["id"]},
                    {"$set": {
                        "status": "failed",
                        "error_message": "Failed to send email"
                    }}
                )
        except Exception as e:
            logger.error(f"Error processing notification {notif['id']}: {e}")
            await db.notifications.update_one(
                {"id": notif["id"]},
                {"$set": {"status": "failed", "error_message": str(e)}}
            )

# Initialize scheduler
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    # Schedule notification processing every minute
    scheduler.add_job(process_pending_notifications, 'interval', minutes=1)
    scheduler.start()
    logger.info("Notification scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    client.close()
    logger.info("Scheduler and database connection closed")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
