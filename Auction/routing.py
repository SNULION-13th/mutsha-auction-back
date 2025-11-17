# Auction/routing.py

from django.urls import path
from . import consumer

websocket_urlpatterns = [
    path('ws/auction/<int:auction_id>/', consumer.AuctionConsumer.as_asgi()),
    path('ws/notifications/', consumer.NotificationConsumer.as_asgi()),
]
