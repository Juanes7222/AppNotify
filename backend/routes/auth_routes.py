from fastapi import APIRouter, Depends
from utils import verify_firebase_token, get_or_create_user

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    """Dependency to get database - will be set by main app"""
    from server import db
    return db


@router.post("/verify")
async def verify_token(user_info: dict = Depends(verify_firebase_token)):
    db = get_db()
    user = await get_or_create_user(user_info, db)
    return {"user": user, "message": "Authentication successful"}


@router.get("/me")
async def get_current_user(user_info: dict = Depends(verify_firebase_token)):
    from fastapi import HTTPException
    db = get_db()
    user = await db.users.find_one({"firebase_uid": user_info["uid"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
