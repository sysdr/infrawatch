"""Service container for shared service instances"""
from services.notification_service import NotificationService
from services.websocket_manager import WebSocketManager

# Shared service instances
notification_service = NotificationService()
websocket_manager = WebSocketManager()

