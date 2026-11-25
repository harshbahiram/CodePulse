from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes.health import router as health_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered GitHub Repository Auditor",
    debug=settings.DEBUG
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)


app.include_router(
    health_router,
    prefix=settings.API_V1_PREFIX
)


@app.get("/")
def root():
    return {
        "message": "Welcome to CodePulse API",
        "version": settings.APP_VERSION,
        "documentation": "/docs"
    }