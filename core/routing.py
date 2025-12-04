# core/routing.py
from django.urls import path
from .consumers import VendorNotificationConsumer  # Existing vendor consumer
from .CarTrackingConsumer import CarTrackingConsumer  # Your separate CarTrackingConsumer

websocket_urlpatterns = [
    path("ws/vendor/notifications/", VendorNotificationConsumer.as_asgi()),
    path("ws/car_tracking/", CarTrackingConsumer.as_asgi()),
]
