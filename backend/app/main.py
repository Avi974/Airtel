"""
Project Udyam Digital - Accel Telecom B2B Main Application.
FastAPI modular monolith matching the V5.2 Architecture Blueprint.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import (
    sessions,
    advisor,
    catalogue,
    quotes,
    consents,
    kyc,
    orders,
    simulator,
    partner,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they do not exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Digital-first acquisition and onboarding journey for Indian MSMEs in one sitting.",
    version="5.2.0",
    lifespan=lifespan,
)

# CORS Middleware for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All 23 Endpoints across 9 Modular Routers
app.include_router(sessions.router, prefix=settings.API_V1_STR)
app.include_router(advisor.router, prefix=settings.API_V1_STR)
app.include_router(catalogue.router, prefix=settings.API_V1_STR)
app.include_router(quotes.router, prefix=settings.API_V1_STR)
app.include_router(consents.router, prefix=settings.API_V1_STR)
app.include_router(kyc.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(simulator.router, prefix=settings.API_V1_STR)
app.include_router(partner.router, prefix=settings.API_V1_STR)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": "5.2.0-airtight",
        "compliance": "DPDP Act 2023 Compliant",
    }
