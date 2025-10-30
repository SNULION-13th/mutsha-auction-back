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

from .serializers import (
    PayReadyRequestSerializer,
    PayApproveRequestSerializer,
    PayReadyResponseSerializer,
    PayApproveResponseSerializer,
    PaymentHistorySerializer,
)

### 등록된 환경변수 정보 가져오기
from django.conf import settings

### 환경변수로 등록된 값 중, KAKAO_PAY_KEY 값 가져와 변수에 넣기
pay_key = settings.KAKAO_PAY_KEY
cid = settings.KAKAO_PAY_CID

### 결제 준비 API 요청 URL 정의하기
payready_url = "https://open-api.kakaopay.com/online/v1/payment/ready"
### 이건 나중에 결제 승인 API 요청시 사용될 URL !
payapprove_url = "https://open-api.kakaopay.com/online/v1/payment/approve"

pay_header = {
    "Content-Type": "application/json",
    "Authorization": f"SECRET_KEY {pay_key}",
}


class PayReadyView(APIView):
    def post(self, request):
        pay_data = request.data
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED
            )

        pay_data["cid"] = cid
        pay_data = json.dumps(pay_data)

        response = requests.post(payready_url, headers=pay_header, data=pay_data)
        response_data = response.json()
        print("결제 준비 응답 데이터:", response_data)

        ### 🔻 이 부분 추가 ###
        if response.status_code == 200:
            item_name = request.data["item_name"]
            point_amount = int(item_name)

            Payment.objects.create(
                tid=response_data["tid"],
                partner_order_id=request.data["partner_order_id"],
                partner_user_id=request.data["partner_user_id"],
                point=point_amount,
                price=request.data["total_amount"],
                user=user,
            )

        return Response(response.json(), status=response.status_code)


class PayApproveView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED
            )

        pg_token = request.data["pg_token"]
        tid = request.data["tid"]

        pay_hist = Payment.objects.get(tid=tid)
        pay_data = {
            "cid": cid,
            "tid": tid,
            "partner_order_id": pay_hist.partner_order_id,
            "partner_user_id": pay_hist.partner_user_id,
            "pg_token": pg_token,
        }
        pay_data = json.dumps(pay_data)
        response = requests.post(payapprove_url, headers=pay_header, data=pay_data)

        ### 🔻 이 부분 추가 ###
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
                        userprofile = UserProfile.objects.select_for_update().get(
                            user=user
                        )

                        # 포인트 업데이트 (이미 승인된 결제가 아닌 경우에만)
                        point_info = {
                            "old_points": userprofile.remaining_points,
                            "added_points": 0,
                            "new_points": userprofile.remaining_points,
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
                                "old_points": old_points,
                                "added_points": added_points,
                                "new_points": new_points,
                            }

                        # 결제 상태 업데이트 및 Kakao 응답 필드 저장
                        pay_hist.pay_status = "approved"

                        # Extract fields from Kakao approve response
                        pay_hist.item_name = response_data.get("item_name")

                        # amount는 중첩된 객체
                        amount_info = response_data.get("amount", {})
                        pay_hist.amount = amount_info.get("total")

                        # payment_method_type은 card_info 또는 직접 제공
                        card_info = response_data.get("card_info", {})
                        pay_hist.payment_method_type = response_data.get(
                            "payment_method_type"
                        ) or card_info.get("card_type", "UNKNOWN")

                        # approved_at은 ISO 8601 형식 문자열
                        approved_at_str = response_data.get("approved_at")
                        if approved_at_str:
                            from django.utils.dateparse import parse_datetime

                            pay_hist.approved_at = parse_datetime(approved_at_str)

                        pay_hist.save()

                    response_data["point_info"] = point_info
                    return Response(response_data, status=response.status_code)

                except (OperationalError, IntegrityError) as e:
                    if attempt < max_retries - 1:
                        # 데이터베이스 잠금 오류 시 재시도
                        print(f"Database lock error (attempt {attempt + 1}): {e}")
                        time.sleep(retry_delay * (2**attempt))  # 지수 백오프
                        continue
                    else:
                        # 최대 재시도 횟수 초과
                        print(f"Database error after {max_retries} attempts: {e}")
                        return Response(
                            {
                                "detail": "결제 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
                            },
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                except Exception as e:
                    # 기타 예상치 못한 오류
                    print(f"Unexpected error in payment approval: {e}")
                    return Response(
                        {
                            "detail": "결제 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

        return Response(response.json(), status=response.status_code)


class PaymentHistoryAPIView(APIView):
    @swagger_auto_schema(
        operation_id="결제 내역 조회 (API)",
        operation_description="사용자의 결제 내역을 조회합니다.",
        responses={
            200: PaymentHistorySerializer(many=True),
            401: "please signin",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="access token",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED
            )

        payments = Payment.objects.filter(user=user).order_by("-id")
        serializer = PaymentHistorySerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentHistoryPageView(APIView):
    """결제 내역을 보여주는 HTML 페이지"""

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "please signin."}, status=status.HTTP_401_UNAUTHORIZED
            )

        payments = Payment.objects.filter(user=user).order_by("-id")
        return render(request, "payment/history.html", {"payments": payments})
