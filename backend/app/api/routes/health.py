import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.database.connection import get_db


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("")
def health_check():
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }


@router.get("/db")
def database_health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "PostgreSQL",
            "connection": "successful"
        }

    except SQLAlchemyError:
        logger.exception("Database health check failed")

        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )