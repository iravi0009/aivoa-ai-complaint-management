from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.complaints import router as complaints_router
from app.db.database import Base, engine
from app.models.complaint import Complaint
from app.api.ai import router as ai_router
from app.api.investigations import router as investigations_router
from app.api.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AIVOA.AI Complaint Management API",
    version="1.0.0",
    description=(
        "AI-powered pharmaceutical customer complaint "
        "management system."
    ),
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(complaints_router)
app.include_router(ai_router)
app.include_router(investigations_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {
        "message": "AIVOA.AI Complaint Management API",
        "status": "running",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "aivoa-backend",
    }