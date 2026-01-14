from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from models import DashboardStats
from utils import verify_firebase_token

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_db():
    """Dependency to get database - will be set by main app"""
    from server import db
    return db


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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


@router.get("/next-event")
async def get_next_event(user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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


@router.get("/recent-activity")
async def get_recent_activity(user_info: dict = Depends(verify_firebase_token), limit: int = 10):
    db = get_db()
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
