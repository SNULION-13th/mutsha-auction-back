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

from .serializers import (
    PayReadyRequestSerializer,
    PayApproveRequestSerializer,
    PayReadyResponseSerializer,
    PayApproveResponseSerializer,
)

# 등록된 환경변수 정보 가져오기
from django.conf import settings

# 환경변수로 등록된 값 중, KAKAO_PAY_KEY 값 가져와 변수에 넣기
pay_key = settings.KAKAO_PAY_KEY
cid = settings.KAKAO_PAY_CID

# 결제 준비 API 요청 URL 정의하기
payready_url = "https://open-api.kakaopay.com/online/v1/payment/ready"
# 결제 승인 API 요청 URL
payapprove_url = "https://open-api.kakaopay.com/online/v1/payment/approve"
# 결제 조회 API 요청 URL
payorder_url = "https://open-api.kakaopay.com/online/v1/payment/order"

pay_header = {
    "Content-Type": "application/json",
    "Authorization": f"SECRET_KEY {pay_key}",
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
        pay_data["cid"] = cid
        pay_data = json.dumps(pay_data)

        #### 4
        response = requests.post(payready_url, headers=pay_header, data=pay_data)
        response_data = response.json()

        # 결제 준비 성공 시 결제 히스토리 생성
        if response.status_code == 200:
            item_name = request.data.get("item_name")
            try:
                point_amount = int(item_name)
            except (TypeError, ValueError):
                point_amount = 0

            Payment.objects.create(
                tid=response_data.get("tid"),
                partner_order_id=request.data.get("partner_order_id"),
                partner_user_id=request.data.get("partner_user_id"),
                point=point_amount,
                price=request.data.get("total_amount"),
                user=user,
            )

        return Response(response_data, status=response.status_code)


class PayApproveView(APIView):
    def post(self, request):
        #### 1
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)

        #### 2
        pg_token = request.data.get("pg_token")
        tid = request.data.get("tid")

        #### 3: 결제 정보 조회
        try:
            pay_hist = Payment.objects.get(tid=tid)
        except Payment.DoesNotExist:
            return Response({"detail": "payment not found."}, status=status.HTTP_404_NOT_FOUND)

        pay_data = {
            "cid": cid,
            "tid": tid,
            "partner_order_id": pay_hist.partner_order_id,
            "partner_user_id": pay_hist.partner_user_id,
            "pg_token": pg_token,
        }

        pay_data = json.dumps(pay_data)
        response = requests.post(payapprove_url, headers=pay_header, data=pay_data)

        # 이미 승인된 결제인 경우 처리 (error_code -702)
        if response.status_code == 400:
            try:
                error_data = response.json()
                # "payment is already done!" 에러인 경우
                if error_data.get("error_code") == -702:
                    # DB에서 이미 승인된 결제인지 확인
                    if pay_hist.pay_status == "approved":
                        # 이미 승인된 결제이므로 성공으로 처리
                        userprofile = UserProfile.objects.get(user=user)
                        return Response({
                            "status": "already_approved",
                            "message": "이미 승인된 결제입니다.",
                            "point_info": {
                                "old_points": userprofile.remaining_points,
                                "added_points": 0,
                                "new_points": userprofile.remaining_points,
                            }
                        }, status=status.HTTP_200_OK)
            except:
                pass

        # 결제 승인 실패 시 로깅
        if response.status_code != 200:
            print(f"PayApprove Error: status={response.status_code}, response={response.text}")

        # 결제 승인 성공 시 포인트 반영 (원자적 처리)
        if response.status_code == 200:
            response_data = response.json()

            # 이미 승인된 결제인지 확인
            was_already_approved = pay_hist.pay_status == "approved"

            # 원자적 트랜잭션으로 중복 처리 방지 (재시도 로직 포함)
            max_retries = 3
            retry_delay = 0.1  # 100ms

            for attempt in range(max_retries):
                try:
                    with transaction.atomic():
                        # select_for_update로 동시성 제어
                        userprofile = UserProfile.objects.select_for_update().get(user=user)

                        # 기본 point_info
                        point_info = {
                            "old_points": userprofile.remaining_points,
                            "added_points": 0,
                            "new_points": userprofile.remaining_points,
                        }

                        if not was_already_approved:
                            # 포인트 업데이트 전후 로깅
                            old_points = userprofile.remaining_points
                            added_points = int(pay_hist.point)

                            # 직접 계산하여 업데이트
                            new_points = old_points + added_points
                            userprofile.remaining_points = new_points
                            userprofile.save()

                            point_info = {
                                "old_points": old_points,
                                "added_points": added_points,
                                "new_points": new_points,
                            }

                        # 결제 상태 업데이트
                        pay_hist.pay_status = "approved"
                        pay_hist.save()

                    response_data["point_info"] = point_info
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
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                except Exception as e:
                    # 기타 예상치 못한 오류
                    print(f"Unexpected error in payment approval: {e}")
                    return Response(
                        {"detail": "결제 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

        return Response(response.json(), status=response.status_code)


class PaymentHistoryView(APIView):
    """
    결제 내역 조회 API
    카카오페이 결제 조회 API를 사용하여 사용자의 결제 내역을 반환
    """
    def get(self, request):
        #### 1. 사용자 인증 확인
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED)

        #### 2. 사용자의 승인된 결제 내역 조회
        payments = Payment.objects.filter(
            user=user,
            pay_status='approved'
        ).order_by('-id')

        #### 3. 각 결제에 대해 카카오페이 API로 상세 정보 조회
        payment_history = []
        for payment in payments:
            try:
                # 카카오페이 결제 조회 API 호출
                pay_data = {
                    "cid": cid,
                    "tid": payment.tid,
                }
                pay_data_json = json.dumps(pay_data)
                response = requests.post(payorder_url, headers=pay_header, data=pay_data_json)

                if response.status_code == 200:
                    kakao_data = response.json()

                    # 응답 데이터에서 필요한 정보 추출
                    payment_info = {
                        "id": payment.id,
                        "tid": payment.tid,
                        "item_name": kakao_data.get("item_name", ""),
                        "amount": kakao_data.get("amount", {}).get("total", 0),
                        "payment_method_type": kakao_data.get("payment_method_type", ""),
                        "approved_at": kakao_data.get("approved_at", ""),
                        "partner_order_id": kakao_data.get("partner_order_id", ""),
                        "partner_user_id": kakao_data.get("partner_user_id", ""),
                        "quantity": kakao_data.get("quantity", 1),
                        "created_at": kakao_data.get("created_at", ""),
                    }
                    payment_history.append(payment_info)
                else:
                    # 카카오페이 API 호출 실패 시 DB 데이터로 대체
                    payment_info = {
                        "id": payment.id,
                        "tid": payment.tid,
                        "item_name": f"{payment.point}P",
                        "amount": payment.price,
                        "payment_method_type": "CARD",
                        "approved_at": "",
                        "partner_order_id": payment.partner_order_id,
                        "partner_user_id": payment.partner_user_id,
                        "quantity": 1,
                        "created_at": "",
                    }
                    payment_history.append(payment_info)
            except Exception as e:
                print(f"Error fetching payment detail for tid {payment.tid}: {e}")
                # 에러 발생 시 DB 데이터로 대체
                payment_info = {
                    "id": payment.id,
                    "tid": payment.tid,
                    "item_name": f"{payment.point}P",
                    "amount": payment.price,
                    "payment_method_type": "CARD",
                    "approved_at": "",
                    "partner_order_id": payment.partner_order_id,
                    "partner_user_id": payment.partner_user_id,
                    "quantity": 1,
                    "created_at": "",
                }
                payment_history.append(payment_info)

        return Response(payment_history, status=status.HTTP_200_OK)
