from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from utils import verify_firebase_token, get_or_create_user

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    """Dependency to get database - will be set by main app"""
    from server import db
    return db


class UserSettingsUpdate(BaseModel):
    timezone: str


@router.post("/verify")
async def verify_token(user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
    user = await get_or_create_user(user_info, db)
    return {"user": user, "message": "Authentication successful"}


@router.get("/me")
async def get_current_user(user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/me")
async def update_user_settings(
    settings: UserSettingsUpdate,
    user_info: dict = Depends(verify_firebase_token)
):
    """Update user settings like timezone"""
    db = get_db()
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = settings.model_dump(exclude_unset=True)
    
    await db.users.update_one(
        {"firebase_uid": user_info["uid"]},
        {"$set": update_data}
    )
    
    updated_user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    return updated_user
