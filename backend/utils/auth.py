import os
import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import User

security = HTTPBearer(auto_error=False)
FIREBASE_VERIFY_URL = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo"


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


async def get_or_create_user(user_info: dict, db) -> dict:
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
    
    # Remove _id if it was added by MongoDB
    user_dict.pop('_id', None)
    return user_dict
