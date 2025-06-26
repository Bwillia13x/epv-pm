"""
FastAPI application providing REST endpoints for EPV Research Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

from src.api.routers import analysis, sockets, market, risk
from src.auth.auth import auth_backend
from src.auth.db import User, create_db_and_tables
from src.auth.manager import get_user_manager
from src.auth.schemas import UserCreate, UserRead, UserUpdate
from fastapi_users import FastAPIUsers
from src.api.middleware import RequestIDMiddleware, ErrorHandlingMiddleware
from src.api.settings import settings

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="REST API for Earnings Power Value analysis and financial research",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

app.include_router(analysis.router, prefix="/api/v1")
app.include_router(sockets.router)
app.include_router(market.router, prefix="/api/v1")
app.include_router(risk.router, prefix="/api/v1")

fastapi_users = FastAPIUsers[User, int](
    get_user_manager, 
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()

@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "message": settings.app_name,
        "version": "1.0.0",
        "endpoints": {
            "analysis": "/api/v1/analysis/{symbol}",
            "batch": "/api/v1/batch",
            "portfolio": "/api/v1/portfolio/optimize",
            "company": "/api/v1/company/{symbol}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)