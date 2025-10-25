from django.shortcuts import render
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from UserProfile.models import UserProfile
from django.db import transaction, IntegrityError
from django.db.utils import OperationalError
import time
import requests
import json


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import PayReadyRequestSerializer, PayApproveRequestSerializer, PayReadyResponseSerializer, PayApproveResponseSerializer

### 등록된 환경변수 정보 가져오기
from django.conf import settings

### 환경변수로 등록된 값 중, KAKAO_PAY_KEY 값 가져와 변수에 넣기
pay_key = settings.KAKAO_PAY_KEY
cid = settings.KAKAO_PAY_CID

### 결제 준비 API 요청 URL 정의하기
payready_url = 'https://open-api.kakaopay.com/online/v1/payment/ready'
### 이건 나중에 결제 승인 API 요청시 사용될 URL !
payapprove_url = 'https://open-api.kakaopay.com/online/v1/payment/approve'

pay_header = {
    'Content-Type': 'application/json',
    'Authorization': f'SECRET_KEY {pay_key}'
}

class PayReadyView(APIView):
    def post(self, request):
		    #### 1
        pay_data = request.data

				#### 2
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)
        
        #### 3
        pay_data['cid'] = cid
        pay_data = json.dumps(pay_data)

				#### 4
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
  def post(self, request):

    #### 1
    user = request.user
    if not user.is_authenticated:
        return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)

    #### 2
    pg_token = request.data['pg_token']
    tid = request.data['tid']
    
    #### 3
    pay_hist = Payment.objects.get(tid=tid)
    pay_data = {
        'cid': cid,
        'tid': tid,
        'partner_order_id': pay_hist.partner_order_id,
        'partner_user_id': pay_hist.partner_user_id,
        'pg_token': pg_token
    }
    
    #### 3
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
                    
                    # 결제 상태 업데이트
                    pay_hist.pay_status = 'approved'
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

class PayOrderDetailView(APIView):
    """
    GET /payment/order/?tid=...   (프로젝트 루트 url include 경로에 따라 /api/payment/order/ 일 수도 있음)
    카카오페이 '주문 조회' API를 서버에서 호출하여,
    과제에 필요한 필드를 추려서 반환.
    """
    def get(self, request):
        tid = request.GET.get("tid")
        if not tid:
            return Response({"error": "tid is required"}, status=status.HTTP_400_BAD_REQUEST)

        order_url = "https://open-api.kakaopay.com/online/v1/payment/order"
        body = json.dumps({"cid": cid, "tid": tid})

        try:
            resp = requests.post(order_url, headers=pay_header, data=body, timeout=10)
        except requests.RequestException as e:
            return Response({"error": "kakaopay request failed", "detail": str(e)}, status=502)

        if resp.status_code != 200:
            # 카카오 응답 원문도 같이 반환 -> 디버깅 편함
            return Response({"error": "kakaopay order inquiry failed",
                             "status": resp.status_code,
                             "detail": resp.text}, status=resp.status_code)

        data = resp.json()

        # amount는 객체(total/discount 등)일 수 있어서 그대로와 total 둘 다 제공
        payload = {
            "tid": data.get("tid"),
            "item_name": data.get("item_name"),
            "amount": data.get("amount"),
            "amount_total": (data.get("amount") or {}).get("total"),
            "payment_method_type": data.get("payment_method_type"),
            "approved_at": data.get("approved_at"),
        }
        return Response(payload, status=200)
    

class PaymentReceiptView(APIView):
    """
    GET /payment/receipt/?tid=...  
    tid로 결제 상세 정보를 반환 (카카오페이 주문 조회 API 사용)
    """
    def get(self, request):
        tid = request.GET.get("tid")
        if not tid:
            return Response({"error": "tid is required"}, status=status.HTTP_400_BAD_REQUEST)

        order_url = "https://open-api.kakaopay.com/online/v1/payment/order"
        body = json.dumps({"cid": cid, "tid": tid})

        try:
            resp = requests.post(order_url, headers=pay_header, data=body, timeout=10)
        except requests.RequestException as e:
            return Response({"error": "kakaopay request failed", "detail": str(e)}, status=502)

        if resp.status_code != 200:
            return Response(
                {"error": "kakaopay order inquiry failed", "detail": resp.text},
                status=resp.status_code,
            )

        data = resp.json()
        payload = {
            "tid": data.get("tid"),
            "item_name": data.get("item_name"),
            "amount": data.get("amount"),
            "amount_total": (data.get("amount") or {}).get("total"),
            "payment_method_type": data.get("payment_method_type"),
            "approved_at": data.get("approved_at"),
        }
        return Response(payload, status=200)
    