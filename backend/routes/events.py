from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timezone
from models import Event, EventCreate, EventUpdate
from utils import verify_firebase_token
from utils import regenerate_notifications

router = APIRouter(prefix="/events", tags=["events"])


def get_db():
    """Dependency to get database - will be set by main app"""
    from server import db
    return db


@router.get("", response_model=List[dict])
async def get_events(user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    events = await db.events.find({"user_id": user["id"]}, {"_id": 0}).sort("event_date", 1).to_list(1000)
    
    # Add subscriber count to each event
    for event in events:
        event["subscribers_count"] = await db.subscriptions.count_documents({"event_id": event["id"]})
    
    return events


@router.post("", response_model=dict)
async def create_event(event_data: EventCreate, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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
    
    # Remove _id if it was added by MongoDB
    event_dict.pop('_id', None)
    event_dict["subscribers_count"] = 0
    return event_dict


@router.get("/{event_id}", response_model=dict)
async def get_event(event_id: str, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    event = await db.events.find_one({"id": event_id, "user_id": user["id"]}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event["subscribers_count"] = await db.subscriptions.count_documents({"event_id": event_id})
    return event


@router.put("/{event_id}", response_model=dict)
async def update_event(event_id: str, event_data: EventUpdate, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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
        await regenerate_notifications(event_id, user["id"], db)
    
    await db.events.update_one({"id": event_id}, {"$set": update_data})
    
    updated_event = await db.events.find_one({"id": event_id}, {"_id": 0})
    updated_event["subscribers_count"] = await db.subscriptions.count_documents({"event_id": event_id})
    return updated_event


@router.delete("/{event_id}")
async def delete_event(event_id: str, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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
