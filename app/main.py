from fastapi import FastAPI
from routes import defect_routes, maintenance_routes, quality_routes

app = FastAPI(title="AI-Powered Quality Control")

# Register routes
app.include_router(defect_routes.router, prefix="/defects")
app.include_router(maintenance_routes.router, prefix="/maintenance")
app.include_router(quality_routes.router, prefix="/quality")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI-Powered Quality Control API"}
