import json
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Auction
from .consumers import AuctionConsumer
from django.utils import timezone
import asyncio
from seminar.asgi import application

class AuctionConsumerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """테스트에 필요한 초기 데이터 설정"""
        cls.seller = User.objects.create_user(username='seller', password='password')
        cls.auction = Auction.objects.create(
            seller=cls.seller,
            title='Test Auction',
            description='A test auction item.',
            starting_price=100,
            current_price=100,
            end_time=timezone.now() + timezone.timedelta(days=1)
        )

    async def test_auction_update_broadcast(self):
        """
        auction_update 이벤트가 consumer를 통해 클라이언트에 정상적으로 방송되는지 테스트합니다.
        """
        # 전체 ASGI 애플리케이션을 사용하여 WebsocketCommunicator를 생성합니다.
        communicator = WebsocketCommunicator(
            application,
            f"/ws/auction/{self.auction.id}/"
        )
        
        # 웹소켓에 연결합니다.
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected, "웹소켓 연결에 실패했습니다.")

        # 테스트를 위해 channel layer를 가져옵니다.
        channel_layer = get_channel_layer()

        # 방송할 테스트 데이터 정의
        update_data = {
            "auction_id": self.auction.id,
            "current_price": 150,
            "message": "새로운 입찰이 등록되었습니다!"
        }

        # channel layer를 통해 직접 그룹에 메시지를 보냅니다.
        # 실제 애플리케이션에서는 이 부분이 입찰을 처리하는 View 함수에 위치하게 됩니다.
        await channel_layer.group_send(
            f"auction_{self.auction.id}",
            {
                "type": "auction.update", # consumer의 `auction_update` 메소드를 호출
                "data": update_data
            }
        )

        # consumer로부터 메시지를 수신합니다.
        response = await communicator.receive_json_from()

        # 수신한 데이터가 보낸 데이터와 일치하는지 확인합니다.
        self.assertEqual(response, update_data)

        # 웹소켓 연결을 종료합니다.
        await communicator.disconnect()

    async def test_multiple_users_receive_broadcast(self):
        """
        여러 명의 사용자가 접속했을 때 모두에게 정상적으로 방송되는지 테스트합니다.
        """
        # 2개의 클라이언트를 시뮬레이션하기 위해 2개의 Communicator를 생성합니다.
        communicator1 = WebsocketCommunicator(application, f"/ws/auction/{self.auction.id}/")
        communicator2 = WebsocketCommunicator(application, f"/ws/auction/{self.auction.id}/")

        # 두 클라이언트 모두 웹소켓에 연결합니다.
        connected1, _ = await communicator1.connect()
        connected2, _ = await communicator2.connect()
        self.assertTrue(connected1, "클라이언트 1이 연결에 실패했습니다.")
        self.assertTrue(connected2, "클라이언트 2가 연결에 실패했습니다.")

        # 채널 레이어를 가져옵니다.
        channel_layer = get_channel_layer()

        # 방송할 테스트 데이터를 정의합니다.
        update_data = {
            "auction_id": self.auction.id,
            "current_price": 200,
            "message": "새로운 입찰이 발생했습니다!"
        }

        # 채널 레이어를 통해 그룹에 메시지를 보냅니다.
        await channel_layer.group_send(
            f"auction_{self.auction.id}",
            {
                "type": "auction.update",
                "data": update_data
            }
        )

        # 두 클라이언트 모두 메시지를 수신하는지 확인합니다.
        response1 = await communicator1.receive_json_from()
        response2 = await communicator2.receive_json_from()
        
        self.assertEqual(response1, update_data)
        self.assertEqual(response2, update_data)

        # 웹소켓 연결을 종료합니다.
        await communicator1.disconnect()
        await communicator2.disconnect()