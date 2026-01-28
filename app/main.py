"""FastAPI application factory with router registration."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base
from app import models  # noqa: F401 - Import to register models with Base

# Import all routers
from app.routers import (
    pages,
    auth,
    students,
    departments,
    subjects,
    results,
    fees,
    clearance,
    announcements,
    profile,
    dashboard,
)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-ready FastAPI backend for managing students, departments, subjects, results, fees, and clearance.",
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Register routers
    app.include_router(pages.router)
    app.include_router(auth.router)
    app.include_router(students.router)
    app.include_router(departments.router)
    app.include_router(subjects.router)
    app.include_router(results.router)
    app.include_router(fees.router)
    app.include_router(clearance.router)
    app.include_router(announcements.router)
    app.include_router(profile.router)
    app.include_router(dashboard.router)
    
    return app


# Create app instance
app = create_app()
