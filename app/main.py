from fastapi import FastAPI
from routes import defect_routes, maintenance_routes, quality_routes
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
def read_root():
    return {"message": "Welcome to AI-Powered Quality Control API"}

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy", "version": app.version}

@app.get("/version")
def get_version():
    """
    Endpoint to retrieve the current API version.
    """
    return {"version": app.version}
