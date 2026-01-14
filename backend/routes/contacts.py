from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timezone
from models import Contact, ContactCreate
from utils import verify_firebase_token

router = APIRouter(prefix="/contacts", tags=["contacts"])


def get_db():
    """Dependency to get database - will be set by main app"""
    from server import db
    return db


@router.get("", response_model=List[dict])
async def get_contacts(user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    contacts = await db.contacts.find({"user_id": user["id"]}, {"_id": 0}).to_list(1000)
    
    # Mark the user's own contact
    for contact in contacts:
        if contact["email"] == user["email"]:
            contact["is_self"] = True
            contact["display_name"] = "Tú"
        else:
            contact["is_self"] = False
            contact["display_name"] = contact["name"]
    
    return contacts


@router.post("", response_model=dict)
async def create_contact(contact_data: ContactCreate, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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
    
    # Remove _id if it was added by MongoDB
    contact_dict.pop('_id', None)
    return contact_dict


@router.get("/{contact_id}", response_model=dict)
async def get_contact(contact_id: str, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    contact = await db.contacts.find_one({"id": contact_id, "user_id": user["id"]}, {"_id": 0})
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact


@router.put("/{contact_id}", response_model=dict)
async def update_contact(contact_id: str, contact_data: ContactCreate, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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


@router.delete("/{contact_id}")
async def delete_contact(contact_id: str, user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
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
