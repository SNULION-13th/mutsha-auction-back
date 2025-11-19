import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Auction


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # 글로벌 그룹에 연결
        self.global_group_name = "global_notifications"
        
        await self.channel_layer.group_add(
            self.global_group_name, 
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        # 글로벌 그룹에서 제거
        await self.channel_layer.group_discard(
            self.global_group_name, 
            self.channel_name
        )
    
    async def auction_created(self, event):
        # 경매 생성 알림을 클라이언트로 전송
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