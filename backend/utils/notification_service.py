import logging
from datetime import datetime, timezone, timedelta
from models import ReminderInterval, Notification, Subscription
from utils import send_email, generate_reminder_email

logger = logging.getLogger(__name__)


def calculate_notification_time(event_date: datetime, interval: ReminderInterval) -> datetime:
    """Calculate when a notification should be sent based on event date and interval"""
    if isinstance(event_date, str):
        event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
    
    # Ensure event_date has timezone info (assume UTC if naive)
    if event_date.tzinfo is None:
        event_date = event_date.replace(tzinfo=timezone.utc)
    
    # Handle custom date reminders
    if interval.unit == 'custom' and interval.custom_date:
        scheduled = interval.custom_date
        if isinstance(scheduled, str):
            scheduled = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
        if scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
        return scheduled
    
    # Handle interval-based reminders
    if interval.unit == 'minutes':
        scheduled = event_date - timedelta(minutes=interval.value)
    elif interval.unit == 'hours':
        scheduled = event_date - timedelta(hours=interval.value)
    elif interval.unit == 'days':
        scheduled = event_date - timedelta(days=interval.value)
    elif interval.unit == 'weeks':
        scheduled = event_date - timedelta(weeks=interval.value)
    else:
        scheduled = event_date
    
    # Ensure result has UTC timezone
    if scheduled.tzinfo is None:
        scheduled = scheduled.replace(tzinfo=timezone.utc)
    
    return scheduled


async def generate_notifications_for_subscription(event: dict, subscription: Subscription, user_id: str, db):
    """Generate notification documents for a new subscription"""
    logger.info(f"Generating notifications for event {event['id']}, subscription {subscription.id}")
    
    event_date = event['event_date']
    if isinstance(event_date, str):
        event_date = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
    
    logger.info(f"Event date: {event_date}, Reminder intervals: {event.get('reminder_intervals', [])}")
    
    notification_count = 0
    for interval in event.get('reminder_intervals', []):
        interval_obj = ReminderInterval(**interval) if isinstance(interval, dict) else interval
        scheduled_at = calculate_notification_time(event_date, interval_obj)
        
        logger.info(f"Calculated scheduled_at: {scheduled_at}, Current time: {datetime.now(timezone.utc)}")
        
        # Only create notification if it's in the future or very close (within 2 minutes)
        now = datetime.now(timezone.utc)
        time_until_notification = (scheduled_at - now).total_seconds()
        
        # Allow notifications scheduled for now or up to 2 minutes in the future
        # Also allow notifications up to 1 minute in the past (in case of processing delays)
        if time_until_notification >= -60:
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
            notification_count += 1
            logger.info(f"Created notification {notification.id} scheduled for {scheduled_at}")
        else:
            logger.warning(f"Skipping notification - scheduled time {scheduled_at} is in the past")
    
    logger.info(f"Created {notification_count} notifications for subscription {subscription.id}")


async def regenerate_notifications(event_id: str, user_id: str, db):
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
        await generate_notifications_for_subscription(event, subscription, user_id, db)


async def process_pending_notifications(db):
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
            
            # Generate email
            subject, body = generate_reminder_email(event, contact)
            
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
