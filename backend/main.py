from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .config import settings
from .api import temples, meetings, donors

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="寺庙修缮募捐功德纪要系统 - 基于AI的会议转写、摘要生成与募捐文案自动生成系统",
    version=settings.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(temples.router, prefix="/api")
app.include_router(meetings.router, prefix="/api")
app.include_router(donors.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "endpoints": {
            "temples": "/api/temples",
            "meetings": "/api/meetings",
            "donors": "/api/donors",
            "docs": "/docs",
        },
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
