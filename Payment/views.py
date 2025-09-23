from django.shortcuts import render

# Create your views here.

# Create your views here.
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from UserProfile.models import UserProfile
import requests
import json

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import PayReadyRequestSerializer, PayApproveRequestSerializer, PayReadyResponseSerializer, PayApproveResponseSerializer

from django.conf import settings

pay_key = settings.KAKAO_PAY_KEY
cid = settings.KAKAO_PAY_CID

payready_url = 'https://open-api.kakaopay.com/online/v1/payment/ready'
payapprove_url = 'https://open-api.kakaopay.com/online/v1/payment/approve'

pay_header = {
    'Content-Type': 'application/json',
    'Authorization': f'SECRET_KEY {pay_key}'
}

class PayReadyView(APIView):
    @swagger_auto_schema(
        operation_id="카카오페이 단건결제 준비 API",
        operation_description="결제 정보를 카카오페이 서버에 전달하고, 결제 고유번호와 결제 준비 요청에 필요한 URL을 가져옵니다.",
        request_body=PayReadyRequestSerializer,
        responses={200: PayReadyResponseSerializer, 401: "please signin."},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def post(self, request):
        pay_data = request.data

        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)
        
        pay_data['cid'] = cid
        pay_data = json.dumps(pay_data)

        response = requests.post(payready_url, headers=pay_header, data=pay_data)
        response_data = response.json()

        if response.status_code == 200:
            # item_name에서 포인트 수량 추출 (예: "30 잔" -> 30)
            item_name = request.data['item_name']
            point_amount = int(item_name.split()[0])  # "30 잔"에서 "30" 추출
            
            Payment.objects.create(
                tid=response_data['tid'],
                partner_order_id=request.data['partner_order_id'],
                partner_user_id=request.data['partner_user_id'],
                point=point_amount,
                price=request.data['total_amount'],
                user=user
            )

        return Response(response.json(), status=response.status_code)

class PayApproveView(APIView):
    @swagger_auto_schema(
        operation_id="카카오페이 단건결제 승인 API",
        operation_description="""
        사용자가 결제 수단을 선택하고 비밀번호를 입력해 결제 인증을 완료한 뒤, 최종적으로 결제 완료 처리를 요청합니다.
        주의사항: 프론트엔드 없이는 카카오페이 결제창을 띄울 수 없으므로, 해당 API는 스웨거에서 테스트가 어렵습니다.
        """,
        request_body=PayApproveRequestSerializer,
        responses={200: PayApproveResponseSerializer, 401: "please signin."},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)

        pg_token = request.data['pg_token']
        tid = request.data['tid']
        pay_hist = Payment.objects.get(tid=tid)
        pay_data = {
            'cid': cid,
            'tid': tid,
            'partner_order_id': pay_hist.partner_order_id,
            'partner_user_id': pay_hist.partner_user_id,
            'pg_token': pg_token
        }
        pay_data = json.dumps(pay_data)
        response = requests.post(payapprove_url, headers=pay_header, data=pay_data)

        if response.status_code == 200:
            pay_hist.pay_status = 'approved'
            userprofile = UserProfile.objects.get(user=user)
            
            # 포인트 업데이트 전후 로깅
            old_points = userprofile.remaining_points
            added_points = int(pay_hist.point)
            userprofile.remaining_points += added_points
            new_points = userprofile.remaining_points
            
            print(f"결제 승인 완료 - 사용자: {user.username}")
            print(f"포인트 변경: {old_points} -> {new_points} (+{added_points})")
            
            pay_hist.save()
            userprofile.save()
            
            print(f"데이터베이스 저장 완료")
            
            # 응답에 포인트 정보 추가
            response_data = response.json()
            response_data['point_info'] = {
                'old_points': old_points,
                'added_points': added_points,
                'new_points': new_points
            }
            return Response(response_data, status=response.status_code)

        return Response(response.json(), status=response.status_code)