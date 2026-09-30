"""
Analytics API — Dashboard data endpoint.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User
from app.services.user_service import get_current_user
from app.services.analytics_service import get_dashboard_stats, reset_analytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return all analytics data for the Dashboard page.
    Includes overview metrics, query type distribution,
    daily volume trend, and knowledge gap log.
    """
    return get_dashboard_stats(current_user.id, db)

@router.delete("/reset")
def reset_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reset all analytics data for the user.
    """
    reset_analytics(current_user.id, db)
    return {"status": "success", "message": "Analytics reset successfully."}
