"""API Routes Package"""

from .chat import router as chat_router
from .knowledge_base import router as kb_router

__all__ = ["chat_router", "kb_router"]
