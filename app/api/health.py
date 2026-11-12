from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db


router = APIRouter(tags=["Health"])


@router.get("/", summary="Welcome")
def root() -> dict[str, str]:
    """Return a welcome message to show that the API is running."""
    return {"message": "Welcome to Address Book API", "status": "running"}


@router.get("/health", summary="Readiness check")
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Check that the database answers a simple query."""
    db.execute(text("SELECT 1"))
    return {"status": "healthy"}
