from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone

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
    value: Optional[int] = None
    unit: str  # 'minutes', 'hours', 'days', 'weeks', 'custom'
    custom_date: Optional[datetime] = None  # For custom reminders

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