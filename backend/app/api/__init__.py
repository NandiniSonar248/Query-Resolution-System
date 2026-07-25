from app.api.auth import router as auth_router
from app.api.upload import router as upload_router
from app.api.query import router as query_router
from app.api.history import router as history_router
from app.api.analytics import router as analytics_router
from app.api.user import router as user_router

__all__ = [
    "auth_router", "upload_router", "query_router",
    "history_router", "analytics_router", "user_router",
]
