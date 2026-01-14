from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.middleware.gzip import GZipMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from pathlib import Path
import os
import logging
import time


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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de startup
    scheduler.add_job(lambda: process_pending_notifications(db), 'interval', minutes=1)
    scheduler.start()
    logger.info("Notification scheduler started")
    
    yield
    
    # Código de shutdown
    scheduler.shutdown()
    client.close()
    logger.info("Scheduler and database connection closed")

# Create the main app
app = FastAPI(title="Event Reminder System", lifespan=lifespan)

# Create a router with the /api prefix
api_router = APIRouter()

# Basic routes

@api_router.head("/")
@api_router.get("/")
async def root():
    return {"message": "Sistema Iglesia API v1.0", "status": "running"}

@api_router.head("/")
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

# Configure CORS first
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=6)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:.4f}")
    
    # Log slow requests (> 1 segundo)
    if process_time > 1.0:
        logger.warning(f"Slow request: {request.method} {request.url.path} took {process_time:.4f}s")
    
    return response

# Include the router in the main app
app.include_router(api_router)
