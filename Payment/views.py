from django.shortcuts import render
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
payment_detail_url = 'https://open-api.kakaopay.com/online/v1/payment/order'

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
            item_name = request.data['item_name']
            point_amount = int(item_name)
            
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
            response_data = response.json()
            
            # 카카오페이 API 응답에서 상세 정보 추출하여 DB에 저장
            pay_hist.pay_status = 'approved'
            pay_hist.item_name = response_data.get('item_name', '')
            pay_hist.payment_method_type = response_data.get('payment_method_type', '')
            pay_hist.aid = response_data.get('aid', '')
            pay_hist.cid = response_data.get('cid', '')
            pay_hist.sid = response_data.get('sid', '')
            pay_hist.status = response_data.get('status', '')
            pay_hist.quantity = response_data.get('quantity', 1)
            pay_hist.vat_amount = response_data.get('amount', {}).get('vat_amount', 0)
            pay_hist.tax_free_amount = response_data.get('amount', {}).get('tax_free_amount', 0)
            pay_hist.payload = response_data.get('payload', '')
            pay_hist.card_info = response_data.get('card_info', {})
            
            # 날짜 필드 처리
            if response_data.get('created_at'):
                from datetime import datetime
                try:
                    pay_hist.created_at = datetime.fromisoformat(response_data['created_at'].replace('Z', '+00:00'))
                except:
                    pass
            
            if response_data.get('approved_at'):
                from datetime import datetime
                try:
                    pay_hist.approved_at = datetime.fromisoformat(response_data['approved_at'].replace('Z', '+00:00'))
                except:
                    pass
            
            userprofile = UserProfile.objects.get(user=user)
            
            # 포인트 업데이트 전후 로깅
            old_points = userprofile.remaining_points
            added_points = int(pay_hist.point)
            userprofile.remaining_points += added_points
            new_points = userprofile.remaining_points
            
            pay_hist.save()
            userprofile.save()
            
            response_data['point_info'] = {
                'old_points': old_points,
                'added_points': added_points,
                'new_points': new_points
            }
            return Response(response_data, status=response.status_code)

        return Response(response.json(), status=response.status_code)

class PaymentHistoryView(APIView):
    @swagger_auto_schema(
        operation_id="카카오페이 결제 내역 조회 API",
        operation_description="사용자의 카카오페이 결제 내역을 조회합니다.",
        responses={200: "결제 내역 목록", 401: "please signin."},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # 사용자의 결제 내역을 DB에서 가져오기
        payments = Payment.objects.filter(user=user, pay_status='approved').order_by('-id')
        
        payment_history = []
        for i, payment in enumerate(payments):
            
            # 모든 결제에 대해 카카오페이 API 호출
            try:
                # 카카오페이 주문 조회 API는 POST 방식
                detail_data = {
                    'cid': cid,
                    'tid': payment.tid
                }
                detail_data = json.dumps(detail_data)

                
                response = requests.post(payment_detail_url, headers=pay_header, data=detail_data)
                
                if response.status_code == 200:
                    response_data = response.json()
    
                    
                    payment_info = {
                        'tid': payment.tid,
                        'item_name': response_data.get('item_name', ''),
                        'amount': response_data.get('amount', {}).get('total', 0),
                        'payment_method_type': response_data.get('payment_method_type', ''),
                        'approved_at': response_data.get('approved_at', ''),
                        'status': response_data.get('status', ''),
                        'point': payment.point,
                        'price': payment.price
                    }
                    payment_history.append(payment_info)
            except Exception as e:
                # API 호출 실패 시 DB 데이터만으로 구성
                payment_info = {
                    'tid': payment.tid,
                    'item_name': f'{payment.point} 포인트',
                    'amount': payment.price,
                    'payment_method_type': '카카오페이',
                    'approved_at': payment.approved_at.isoformat() if payment.approved_at else '',
                    'status': 'DONE',
                    'point': payment.point,
                    'price': payment.price
                }
                payment_history.append(payment_info)
  
        return Response(payment_history, status=status.HTTP_200_OK)