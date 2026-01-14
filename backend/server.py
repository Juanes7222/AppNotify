from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pathlib import Path
import os
import logging

# Import routes
from routes import auth_routes, contacts, events, subscriptions, notifications, dashboard
from utils import process_pending_notifications

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(
    mongo_url,
    tls=True,
    tlsAllowInvalidCertificates=True
)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Event Reminder System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Basic routes
@api_router.get("/")
async def root():
    return {"message": "Event Reminder System API"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

# Include all route modules
api_router.include_router(auth_routes.router)
api_router.include_router(dashboard.router)
api_router.include_router(contacts.router)
api_router.include_router(events.router)
api_router.include_router(subscriptions.router)
api_router.include_router(notifications.router)

# Initialize scheduler
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    # Schedule notification processing every minute
    scheduler.add_job(lambda: process_pending_notifications(db), 'interval', minutes=1)
    scheduler.start()
    logger.info("Notification scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    client.close()
    logger.info("Scheduler and database connection closed")

# Configure CORS first
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router in the main app
app.include_router(api_router)
