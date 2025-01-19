from fastapi import FastAPI
from routes import defect_routes, maintenance_routes, quality_routes
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Powered Quality Control", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(defect_routes.router, prefix="/defects")
app.include_router(maintenance_routes.router, prefix="/maintenance")
app.include_router(quality_routes.router, prefix="/quality")

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """
    Middleware to log incoming requests and outgoing responses.
    """
    start_time = datetime.now()
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Outgoing response: {response.status_code}, Process time: {process_time:.2f}s")
    return response

# System Health Check Component
def check_system_health():
    """
    Perform a basic system health check.

    Returns:
        dict: System health status.
    """
    try:
        # Simulate a health check (e.g., check database connection, disk space, etc.)
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        logger.info("System health check completed successfully.")
        return health_status
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/")
def read_root():
    return {"message": "Welcome to AI-Powered Quality Control API"}

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return check_system_health()

@app.get("/version")
def get_version():
    """
    Endpoint to retrieve the current API version.
    """
    return {"version": app.version}
