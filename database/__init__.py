# database/__init__.py

from .models import Conversation, Message, create_tables, get_db
from .service import ChatService, chat_service

__all__ = [
    'Conversation',
    'Message', 
    'create_tables',
    'get_db',
    'ChatService',
    'chat_service'
]