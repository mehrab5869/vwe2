from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.routers import admin, gateway, user
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")
        print("Continuing without database connection...")
    yield
    # Shutdown: cleanup if needed
    pass


app = FastAPI(
    title="API Proxy Management Platform",
    description="Admin Dashboard and Public Gateway for API Proxy Management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
import os
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
]
if os.getenv("ADMIN_UI_URL"):
    cors_origins.append(os.getenv("ADMIN_UI_URL"))
if os.getenv("USER_DASHBOARD_URL"):
    cors_origins.append(os.getenv("USER_DASHBOARD_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (health must be before gateway to avoid route conflicts)
app.include_router(admin.router, prefix="/admin/api", tags=["admin"])
app.include_router(user.router, prefix="/user/api", tags=["user"])
app.include_router(gateway.router, prefix="/proxy", tags=["gateway"])

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Root endpoint - API info
@app.get("/")
async def root():
    return {
        "message": "API Proxy Management Platform",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "admin_api": "/admin/api",
            "user_api": "/user/api",
            "gateway": "/proxy/*",
            "docs": "/docs"
        },
        "frontend": {
            "admin_panel": "/admin",
            "user_dashboard": "/user"
        }
    }

# Serve Admin UI
@app.get("/admin", response_class=HTMLResponse)
async def admin_ui():
    try:
        return FileResponse("static/admin/index.html")
    except:
        return HTMLResponse("""
        <h1>Admin Panel</h1>
        <p>Admin UI is being built...</p>
        <p><a href="/admin/api/docs">Admin API Docs</a></p>
        """)

@app.get("/admin/{file_path:path}")
async def admin_static(file_path: str):
    try:
        return FileResponse(f"static/admin/{file_path}")
    except:
        return {"error": "File not found"}

# Serve User Dashboard
@app.get("/user", response_class=HTMLResponse)
async def user_dashboard():
    try:
        return FileResponse("static/user/index.html")
    except:
        return HTMLResponse("""
        <h1>User Dashboard</h1>
        <p>User Dashboard is being built...</p>
        <p><a href="/user/api/docs">User API Docs</a></p>
        """)

@app.get("/user/{file_path:path}")
async def user_static(file_path: str):
    try:
        return FileResponse(f"static/user/{file_path}")
    except:
        return {"error": "File not found"}

# Catch all for any other paths
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def catch_all(path: str, request: Request):
    """Catch all endpoint for debugging"""
    return {
        "message": f"Path '{path}' not found",
        "method": request.method,
        "available_prefixes": ["/admin", "/user", "/proxy", "/docs", "/redoc", "/health"],
        "note": "Try accessing /admin or /user for frontend, /docs for API documentation"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
