from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import Subscription, SubscriptionCreate
from utils import verify_firebase_token
from utils import generate_notifications_for_subscription

router = APIRouter(prefix="/events/{event_id}/subscriptions", tags=["subscriptions"])


def get_db():
    """Dependency to get database - will be set by main app"""
    from server import db
    return db


@router.get("", response_model=List[dict])
async def get_event_subscriptions(event_id: str, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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


@router.post("", response_model=dict)
async def add_subscription(event_id: str, sub_data: SubscriptionCreate, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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
    
    # Remove _id if it was added by MongoDB
    sub_dict.pop('_id', None)
    
    # Generate notifications for this subscription
    await generate_notifications_for_subscription(event, subscription, user["id"], db)
    
    return {**sub_dict, "contact": contact}


@router.delete("/{subscription_id}")
async def remove_subscription(event_id: str, subscription_id: str, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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
