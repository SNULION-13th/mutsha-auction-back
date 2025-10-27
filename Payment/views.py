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
        pay_data = request.data

        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)
        
        pay_data['cid'] = cid
        pay_data = json.dumps(pay_data)
        
        response = requests.post(payready_url, headers=pay_header, data=pay_data)
        response_data = response.json()

				### 🔻 이 부분 추가 ###
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
        
# class PayApproveView(APIView):
#     def post(self, request):
#           user = request.user
#           if not user.is_authenticated:
#               return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)

#           pg_token = request.data['pg_token']
#           tid = request.data['tid']
          
#           pay_hist = Payment.objects.get(tid=tid)
#           pay_data = {
#               'cid': cid,
#               'tid': tid,
#               'partner_order_id': pay_hist.partner_order_id,
#               'partner_user_id': pay_hist.partner_user_id,
#               'pg_token': pg_token
#           }
#           pay_data = json.dumps(pay_data)
#           response = requests.post(payapprove_url, headers=pay_header, data=pay_data)

#           ### 🔻 이 부분 추가 ###
#           if response.status_code == 200:
#               response_data = response.json()
              
#               # 이미 승인된 결제인지 확인
#               was_already_approved = pay_hist.pay_status == 'approved'
              
#               # 원자적 트랜잭션으로 중복 처리 방지 (재시도 로직 포함)
#               max_retries = 3
#               retry_delay = 0.1  # 100ms
              
#               for attempt in range(max_retries):
#                   try:
#                       with transaction.atomic():
#                           # select_for_update로 동시성 제어
#                           userprofile = UserProfile.objects.select_for_update().get(user=user)
                          
#                           # 포인트 업데이트 (이미 승인된 결제가 아닌 경우에만)
#                           point_info = {
#                               'old_points': userprofile.remaining_points,
#                               'added_points': 0,
#                               'new_points': userprofile.remaining_points
#                           }
                          
#                           if not was_already_approved:
#                               # 포인트 업데이트 전후 로깅
#                               old_points = userprofile.remaining_points
#                               added_points = int(pay_hist.point)
                              
#                               # 직접 계산하여 업데이트 (F() 표현식 대신)
#                               new_points = old_points + added_points
#                               userprofile.remaining_points = new_points
#                               userprofile.save()
                              
#                               point_info = {
#                                   'old_points': old_points,
#                                   'added_points': added_points,
#                                   'new_points': new_points
#                               }
                          
#                           # 결제 상태 업데이트
#                           pay_hist.pay_status = 'approved'
#                           pay_hist.save()
                      
#                       response_data['point_info'] = point_info
#                       return Response(response_data, status=response.status_code)
                      
#                   except (OperationalError, IntegrityError) as e:
#                       if attempt < max_retries - 1:
#                           # 데이터베이스 잠금 오류 시 재시도
#                           print(f"Database lock error (attempt {attempt + 1}): {e}")
#                           time.sleep(retry_delay * (2 ** attempt))  # 지수 백오프
#                           continue
#                       else:
#                           # 최대 재시도 횟수 초과
#                           print(f"Database error after {max_retries} attempts: {e}")
#                           return Response(
#                               {"detail": "결제 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}, 
#                               status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                           )
#                   except Exception as e:
#                       # 기타 예상치 못한 오류
#                       print(f"Unexpected error in payment approval: {e}")
#                       return Response(
#                           {"detail": "결제 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}, 
#                           status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                       )

#           return Response(response.json(), status=response.status_code)

class PayApproveView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "please signin."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        pg_token = request.data.get("pg_token")
        tid = request.data.get("tid")
        
        

        if not pg_token or not tid:
            print("❌ 결제 승인 요청 실패: pg_token 또는 tid 없음")
            return Response(
                {"detail": "pg_token 또는 tid가 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pay_hist = Payment.objects.get(tid=tid)
        except Payment.DoesNotExist:
            print(f"❌ Payment 객체 없음: tid={tid}")
            return Response(
                {"detail": f"tid={tid} 에 해당하는 결제 내역이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        pay_data = {
            "cid": cid,
            "tid": tid,
            "partner_order_id": pay_hist.partner_order_id,
            "partner_user_id": pay_hist.partner_user_id,
            "pg_token": pg_token,
        }

        pay_data_json = json.dumps(pay_data)
        print("🟡 KakaoPay 승인 요청 데이터:", pay_data_json)

        # 카카오페이 승인 요청
        response = requests.post(payapprove_url, headers=pay_header, data=pay_data_json)
        print("🟣 KakaoPay 응답 상태코드:", response.status_code)
        print("🟣 KakaoPay 응답 본문:", response.text)

        # ✅ 응답이 200이 아닐 경우, KakaoPay의 상세 에러메시지를 클라이언트에도 전달
        if response.status_code == 400 and "already done" in response.text:
             return Response({"detail": "이미 승인된 결제입니다."}, status=200)
        if response.status_code != 200:
            try:
                err_json = response.json()
            except Exception:
                err_json = {"raw_response": response.text}

            return Response(
                {
                    "detail": "결제 승인 실패",
                    "status_code": response.status_code,
                    "kakao_error": err_json,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ 정상 응답일 경우 포인트 지급 및 상태 갱신
        response_data = response.json()

        was_already_approved = pay_hist.pay_status == "approved"
        max_retries = 3
        retry_delay = 0.1  # 100ms

        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    userprofile = UserProfile.objects.select_for_update().get(user=user)

                    point_info = {
                        "old_points": userprofile.remaining_points,
                        "added_points": 0,
                        "new_points": userprofile.remaining_points,
                    }

                    if not was_already_approved:
                        old_points = userprofile.remaining_points
                        added_points = int(pay_hist.point)
                        new_points = old_points + added_points
                        userprofile.remaining_points = new_points
                        userprofile.save()

                        point_info = {
                            "old_points": old_points,
                            "added_points": added_points,
                            "new_points": new_points,
                        }

                    pay_hist.pay_status = "approved"
                    pay_hist.save()

                response_data["point_info"] = point_info
                print("✅ 결제 승인 및 포인트 갱신 성공:", point_info)
                return Response(response_data, status=status.HTTP_200_OK)

            except (OperationalError, IntegrityError) as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ DB lock error (재시도 {attempt + 1}): {e}")
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    print(f"❌ DB error after {max_retries} attempts: {e}")
                    return Response(
                        {"detail": "DB 오류 발생. 잠시 후 다시 시도해주세요."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            except Exception as e:
                print(f"❌ 예상치 못한 오류 발생: {e}")
                return Response(
                    {"detail": "결제 처리 중 오류가 발생했습니다."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"detail": "결제 승인 처리 실패"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    
# ✅ (1) 실시간 결제내역 동기화 + 저장
class PaySyncOrderView(APIView):
    """
    카카오페이 API에서 사용자의 승인 완료된 결제내역을 실시간으로 가져와
    Payment DB에 저장하는 뷰
    """
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)

        # DB에 저장된 승인된 결제 목록 불러오기
        payments = Payment.objects.filter(user=user, pay_status='approved')

        synced_orders = []
        for pay in payments:
            url = "https://open-api.kakaopay.com/online/v1/payment/order"
            params = {"cid": cid, "tid": pay.tid}
            response = requests.get(url, headers=pay_header, params=params)

            if response.status_code == 200:
                data = response.json()
                pay.item_name = data.get('item_name', pay.item_name)
                pay.price = data.get('amount', {}).get('total', pay.price)
                pay.payment_method_type = data.get('payment_method_type', 'UNKNOWN')
                pay.approved_at = data.get('approved_at', None)
                pay.save()

                synced_orders.append({
                    "tid": pay.tid,
                    "item_name": pay.item_name,
                    "amount": pay.price,
                    "payment_method_type": pay.payment_method_type,
                    "approved_at": pay.approved_at
                })

        return Response({"synced_orders": synced_orders}, status=status.HTTP_200_OK)


# ✅ (2) 저장된 결제내역 리스트 불러오기
class PayOrderListView(APIView):
    """
    DB에 저장된 결제 내역 리스트를 최신순으로 반환
    """
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)

        payments = Payment.objects.filter(user=user, pay_status="approved").order_by("-approved_at")

        result = [
            {
                "tid": p.tid,
                "item_name": p.item_name,
                "amount": p.price,
                "payment_method_type": p.payment_method_type,
                "approved_at": p.approved_at
            }
            for p in payments
        ]
        return Response(result, status=status.HTTP_200_OK)
