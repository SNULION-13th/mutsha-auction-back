import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Auction

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.notifications_group_name = f"notifications_{self.user.id}"
            await self.channel_layer.group_add(
                self.notifications_group_name, self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.notifications_group_name, self.channel_name
        )

    async def auction_created(self, event):
        await self.send_json(event["data"])

        
class AuctionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope["url_route"]["kwargs"]["auction_id"]
        self.auction_group_name = f"auction_{self.auction_id}"

        await self.channel_layer.group_add(
            self.auction_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.auction_group_name, self.channel_name
        )

    async def auction_update(self, event):
        await self.send_json(event["data"])