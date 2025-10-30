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
        # 카카오페이쪽에 보낼 데이터를 완성시켜놓는 것
        pay_data['cid'] = cid
        pay_data = json.dumps(pay_data)

				#### 4
        # 실제 요청. post가 이루어진다.
        # data 담아서 카카오페이쪽에 보내는 것.
        response = requests.post(payready_url, headers=pay_header, data=pay_data)
        response_data = response.json()
        
        ### 🔻 이 부분 추가 ###
        if response.status_code == 200:
          ## pay 성공하면 DB에 해당 결제 내역 정보 저장
            item_name = request.data['item_name']
            point_amount = int(item_name)
            
            Payment.objects.create( 
                                   # 성공하면 프론트 쪽에 반환
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

				### 🔻 이 부분 추가 ###
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
        
        
        
# view의 로직
# 1) 로그인한 사용자(request.user)를 확인합니다.
# 2) DB에서 이 사용자의 모든 Payment 객체를 조회하여 tid 목록을 가져옵니다.
# 3) 각 tid를 가지고 카카오페이 "주문 조회" API를 호출합니다. (requests.get)
# 4) 카카오페이에서 받은 응답들에서 필요한 4가지 정보(item_name, amount, payment_method_type, approved_at)만 골라 리스트에 담습니다.
# 5) 이 리스트를 JsonResponse로 반환합니다.


class PayHistoryView(APIView):
    # 여기서 history data를 client가 get하는 것이므로 get 요청이다.
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED) # 1번 로그인 확인 및 유저 확인
        try:
            user_payments = Payment.objects.filter(user=user, pay_status='approved') # 2번 DB에서 이 사용자의 모든 Payment 객체를 조회하여 tid 목록을 가져옵니다.

        except Payment.DoesNotExist:
            return Response([]) # 빈 리스트를 반환
    
        # 3) 각 tid를 가지고 카카오페이 "주문 조회" API를 호출합니다. (requests.get)
        kakao_api_url = "https://open-api.kakaopay.com/online/v1/payment/order"
        
        payment_history_list = [] # 결국 클라이언트 쪽으로 보낼 response 리스트
        
        # 조회한 Payment 객체들을 하나씩 순회하면서 호출해야함.
        for payment in user_payments:
            
            try:
                # 3-1) 카카오페이 "주문 조회" API 호출 (GET 요청!)
                #      파일 상단에 정의된 pay_header를 사용합니다.
                payload = {
                'cid': cid,           # 파일 상단의 글로벌 변수 cid
                'tid': payment.tid    # DB에서 가져온 tid
            }
                res = requests.post(kakao_api_url, headers=pay_header, data=json.dumps(payload))
                res.raise_for_status() # 200 OK가 아니면 예외 발생

                data = res.json() # 가져온 response를 추출

                # 4) 요구사항에 맞는 4가지 정보만 추출
                payment_info = {
                    "item_name": data.get("item_name"),
                    "amount": data.get("amount", {}).get("total"), # amount 객체 안의 total 금액
                    "payment_method_type": data.get("payment_method_type"),
                    "approved_at": data.get("approved_at"),
                }
                payment_history_list.append(payment_info) # 다 추출해서 정답 리스트에 추가

            except requests.exceptions.RequestException as e:
                # API 호출 실패 시 (네트워크 오류, 4xx/5xx 응답 등)
                print(f"Kakao API Error for tid {payment.tid}: {e}")
                # 해당 건은 무시하고 다음 결제 내역 조회로 넘어갑니다.
                continue
            except Exception as e:
                # 기타 예외 처리
                print(f"Error processing payment {payment.tid}: {e}")
                continue

        # 5) 수집된 모든 결제 내역 리스트를 반환합니다.
        return Response(payment_history_list)