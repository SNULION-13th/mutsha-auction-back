import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Auction

# TODO: class NotificationConsumer(AsyncJsonWebsocketConsumer) 

        
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

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """글로벌 알림을 처리하는 WebSocket Consumer"""
    
    async def connect(self):
        self.notification_group_name = "global_notifications"
        
        await self.channel_layer.group_add(
            self.notification_group_name, 
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.notification_group_name, 
            self.channel_name
        )

    async def auction_created(self, event):
        """새로운 경매가 생성되었을 때 클라이언트로 알림 전송"""
        await self.send_json(event["data"])
    
    async def auction_ended(self, event):
        """경매가 종료되었을 때 클라이언트로 알림 전송"""
        await self.send_json(event["data"])
    
    async def notification(self, event):
        """일반적인 알림을 클라이언트로 전송"""
        await self.send_json(event["data"])