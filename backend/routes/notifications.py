from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
from models import Notification
from utils import verify_firebase_token
from utils import send_email, generate_test_reminder_email, generate_test_smtp_email

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_db():
    """Dependency to get database - will be set by main app"""
    from server import db
    return db


@router.get("", response_model=List[dict])
async def get_notifications(
    user_info: dict = Depends(verify_firebase_token),
    status: Optional[str] = None,
    limit: int = 100
):
    db = get_db()
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


@router.post("/{notification_id}/send-test")
async def send_test_notification(notification_id: str, user_info: dict = Depends(verify_firebase_token)):
    """Send a notification immediately for testing purposes"""
    db = get_db()
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notif = await db.notifications.find_one({
        "id": notification_id,
        "user_id": user["id"]
    }, {"_id": 0})
    
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notif["status"] != "pending":
        raise HTTPException(status_code=400, detail="Can only send pending notifications")
    
    # Get event and contact info
    event = await db.events.find_one({"id": notif["event_id"]}, {"_id": 0})
    contact = await db.contacts.find_one({"id": notif["contact_id"]}, {"_id": 0})
    
    if not event or not contact:
        raise HTTPException(status_code=404, detail="Event or contact not found")
    
    try:
        # Generate test email
        subject, body = generate_test_reminder_email(event, contact)
        
        # Send email
        success = await send_email(contact['email'], subject, body)
        
        if success:
            await db.notifications.update_one(
                {"id": notification_id},
                {"$set": {
                    "status": "sent",
                    "sent_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            return {"message": "Test notification sent successfully", "email": contact['email']}
        else:
            return {"message": "Failed to send test notification", "email": contact['email']}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-email")
async def test_email(user_info: dict = Depends(verify_firebase_token)):
    """Send a test email to verify SMTP configuration"""
    db = get_db()
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        subject, body = generate_test_smtp_email(user)
        success = await send_email(user['email'], subject, body)
        
        if success:
            return {
                "success": True,
                "message": f"Correo de prueba enviado exitosamente a {user['email']}",
                "email": user['email']
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send test email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
