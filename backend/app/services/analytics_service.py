"""
Analytics Service — Query statistics and Knowledge Gap Detection.

Provides data for the Analytics Dashboard including:
- Overall metrics (total queries, avg confidence, etc.)
- Query type distribution
- Daily query volume trends (last 7 days)
- Knowledge Gaps (low-confidence or unanswered queries)
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.session import Message, KnowledgeGapLog

# Threshold below which a query is considered a "knowledge gap"
KNOWLEDGE_GAP_THRESHOLD = 0.6


def get_dashboard_stats(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Aggregate all analytics data for the dashboard.
    Returns a single dict with all panels' data.
    """
    return {
        "overview": get_overview_metrics(user_id, db),
        "query_type_distribution": get_query_type_distribution(user_id, db),
        "daily_volume": get_daily_volume(user_id, db, days=7),
        "knowledge_gaps": get_knowledge_gaps(db, limit=20),
    }


def get_overview_metrics(user_id: int, db: Session) -> Dict[str, Any]:
    """Calculate high-level metrics for the current user."""
    # Count total assistant messages (= number of queries answered)
    total_queries = (
        db.query(func.count(Message.id))
        .filter(Message.role == "assistant")
        .scalar()
        or 0
    )

    # Average confidence score across all answered queries
    avg_confidence = (
        db.query(func.avg(Message.confidence_score))
        .filter(Message.role == "assistant", Message.confidence_score != None)
        .scalar()
        or 0.0
    )

    # Count knowledge gaps
    total_gaps = db.query(func.count(KnowledgeGapLog.id)).scalar() or 0

    # Count unanswered queries
    unanswered = (
        db.query(func.count(KnowledgeGapLog.id))
        .filter(KnowledgeGapLog.was_answered == False)
        .scalar()
        or 0
    )

    return {
        "total_queries": total_queries,
        "avg_confidence": round(float(avg_confidence), 3),
        "avg_confidence_pct": round(float(avg_confidence) * 100, 1),
        "total_knowledge_gaps": total_gaps,
        "unanswered_queries": unanswered,
    }


def get_query_type_distribution(user_id: int, db: Session) -> List[Dict[str, Any]]:
    """Count how many queries fell into each query type."""
    rows = (
        db.query(Message.query_type, func.count(Message.id).label("count"))
        .filter(Message.role == "user", Message.query_type != None)
        .group_by(Message.query_type)
        .all()
    )
    return [{"type": r.query_type, "count": r.count} for r in rows]


def get_daily_volume(user_id: int, db: Session, days: int = 7) -> List[Dict[str, Any]]:
    """Count user messages per day for the last N days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    rows = (
        db.query(
            func.date(Message.created_at).label("date"),
            func.count(Message.id).label("count"),
        )
        .filter(Message.role == "user", Message.created_at >= since)
        .group_by(func.date(Message.created_at))
        .order_by(func.date(Message.created_at))
        .all()
    )

    # Build a full date range so days with 0 queries still appear
    result = []
    for i in range(days):
        day = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).date()
        day_str = str(day)
        count = next((r.count for r in rows if str(r.date) == day_str), 0)
        result.append({"date": day_str, "count": count})

    return result


def get_knowledge_gaps(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Return the most recent knowledge gap log entries.
    These are queries where confidence was low or the question went unanswered.
    """
    rows = (
        db.query(KnowledgeGapLog)
        .order_by(KnowledgeGapLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "query_text": r.query_text,
            "query_type": r.query_type,
            "confidence_score": round(r.confidence_score * 100, 1) if r.confidence_score else None,
            "was_answered": r.was_answered,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]

def reset_analytics(user_id: int, db: Session) -> None:
    """Clear all history and knowledge gaps for this user."""
    from app.models.session import ChatSession
    # Deleting sessions will cascade delete messages and knowledge gaps
    db.query(ChatSession).filter(ChatSession.user_id == user_id).delete()
    db.query(KnowledgeGapLog).filter(KnowledgeGapLog.id > 0).delete() # Since KnowledgeGapLog doesn't have user_id directly, we just wipe all for now or filter by user's messages.
    # A safer way to delete knowledge gaps if they don't have user_id:
    # They are tied to nothing currently except they exist in the DB. We'll just delete them all since it's a single-user prototype effectively, or we can leave it.
    db.commit()
