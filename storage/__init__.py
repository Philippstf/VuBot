# storage/__init__.py

from .device_id import get_device_id, generate_device_id
from .browser_storage import BrowserChatStorage, browser_storage

__all__ = [
    'get_device_id',
    'generate_device_id', 
    'BrowserChatStorage',
    'browser_storage'
]