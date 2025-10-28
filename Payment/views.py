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
from django.db import transaction
from django.db.models import F
from django.db import IntegrityError, OperationalError
from django.utils import timezone
import time

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
        
        try:
            pay_hist = Payment.objects.get(tid=tid)
        except Payment.DoesNotExist:
            return Response(
                {"detail": "결제 정보를 찾을 수 없습니다."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 이미 승인된 결제인지 먼저 확인
        if pay_hist.pay_status == 'approved':
            return Response(
                {"detail": "이미 처리된 결제입니다.", "point_info": {
                    'old_points': 0,
                    'added_points': 0,
                    'new_points': 0
                }}, 
                status=status.HTTP_200_OK
            )
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
            
            # 이미 승인된 결제인지 확인
            was_already_approved = pay_hist.pay_status == 'approved'
            
            # 원자적 트랜잭션으로 중복 처리 방지 (재시도 로직 포함)
            max_retries = 3
            retry_delay = 0.1  # 100ms
            
            for attempt in range(max_retries):
                try:
                    with transaction.atomic():
                        # select_for_update로 동시성 제어
                        userprofile = UserProfile.objects.select_for_update().get(user=user)
                        
                        # 포인트 업데이트 (이미 승인된 결제가 아닌 경우에만)
                        point_info = {
                            'old_points': userprofile.remaining_points,
                            'added_points': 0,
                            'new_points': userprofile.remaining_points
                        }
                        
                        if not was_already_approved:
                            # 포인트 업데이트 전후 로깅
                            old_points = userprofile.remaining_points
                            added_points = int(pay_hist.point)
                            
                            # 직접 계산하여 업데이트 (F() 표현식 대신)
                            new_points = old_points + added_points
                            userprofile.remaining_points = new_points
                            userprofile.save()
                            
                            point_info = {
                                'old_points': old_points,
                                'added_points': added_points,
                                'new_points': new_points
                            }
                        
                        # 결제 상태 및 추가 정보 업데이트
                        pay_hist.pay_status = 'approved'
                        pay_hist.item_name = f"{pay_hist.point}포인트"
                        pay_hist.payment_method_type = response_data.get('payment_method_type', 'CARD')
                        
                        # approved_at 시간 파싱 및 저장
                        approved_at_str = response_data.get('approved_at')
                        if approved_at_str:
                            try:
                                from datetime import datetime
                                pay_hist.approved_at = datetime.fromisoformat(approved_at_str.replace('Z', '+00:00'))
                            except:
                                pay_hist.approved_at = timezone.now()
                        else:
                            pay_hist.approved_at = timezone.now()
                        
                        pay_hist.save()
                    
                    response_data['point_info'] = point_info
                    return Response(response_data, status=response.status_code)
                    
                except (OperationalError, IntegrityError) as e:
                    if attempt < max_retries - 1:
                        # 데이터베이스 잠금 오류 시 재시도
                        print(f"Database lock error (attempt {attempt + 1}): {e}")
                        time.sleep(retry_delay * (2 ** attempt))  # 지수 백오프
                        continue
                    else:
                        # 최대 재시도 횟수 초과
                        print(f"Database error after {max_retries} attempts: {e}")
                        return Response(
                            {"detail": "결제 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                except Exception as e:
                    # 기타 예상치 못한 오류
                    print(f"Unexpected error in payment approval: {e}")
                    return Response(
                        {"detail": "결제 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

        return Response(response.json(), status=response.status_code)

class PaymentHistoryView(APIView):
    @swagger_auto_schema(
        operation_id="카카오페이 주문내역 조회 API",
        operation_description="사용자의 카카오페이 결제 내역을 조회합니다.",
        responses={200: "결제 내역 목록", 401: "please signin."},
        manual_parameters=[openapi.Parameter("Authorization", openapi.IN_HEADER, description="access token", type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # 사용자의 결제 내역 조회 (승인된 결제만)
        payments = Payment.objects.filter(user=user, pay_status='approved').order_by('-created_at')
        
        payment_history = []
        for payment in payments:
            # 기본 결제 정보 구성 (카카오페이 API 호출 없이도 표시)
            base_payment_data = {
                'tid': payment.tid,
                'partner_order_id': payment.partner_order_id,
                'item_name': payment.item_name or f"{payment.point}포인트",
                'amount': {
                    'total': payment.price,
                    'tax_free': 0,
                    'vat': 0,
                    'point': 0,
                    'discount': 0
                },
                'payment_method_type': payment.payment_method_type or 'CARD',
                'point': payment.point,
                'price': payment.price,
                'pay_status': payment.pay_status,
                'created_at': payment.created_at,
                'approved_at': payment.approved_at,
                'order_detail': None
            }
            
            # 카카오페이 API를 통해 상세 정보 조회 (선택적)
            try:
                order_data = {
                    'cid': cid,
                    'tid': payment.tid
                }
                order_data = json.dumps(order_data)
                
                response = requests.post(payment_detail_url, headers=pay_header, data=order_data)
                
                if response.status_code == 200:
                    order_detail = response.json()
                    
                    # 카카오페이 API 응답에서 필요한 정보 추출하여 업데이트
                    amount_info = order_detail.get('amount', {})
                    payment_method = order_detail.get('payment_method_type', 'CARD')
                    
                    base_payment_data.update({
                        'amount': {
                            'total': amount_info.get('total', payment.price),
                            'tax_free': amount_info.get('tax_free', 0),
                            'vat': amount_info.get('vat', 0),
                            'point': amount_info.get('point', 0),
                            'discount': amount_info.get('discount', 0)
                        },
                        'payment_method_type': payment.payment_method_type or payment_method,
                        'approved_at': payment.approved_at or order_detail.get('approved_at'),
                        'order_detail': order_detail
                    })
                    
                print(f"Successfully fetched details for payment {payment.tid}")
            except Exception as e:
                print(f"Error fetching payment detail for tid {payment.tid}: {e}")
                # API 호출 실패해도 기본 정보는 표시
            
            payment_history.append(base_payment_data)
        
        return Response({
            'data': payment_history,
            'total_count': len(payment_history),
            'status': 'success'
        }, status=status.HTTP_200_OK)