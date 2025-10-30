from django.urls import path
from .views import (
    PayReadyView,
    PayApproveView,
    PaymentHistoryAPIView,
    PaymentHistoryPageView,
)

app_name = "payment"
urlpatterns = [
    # CBV url path
    path("ready/", PayReadyView.as_view()),
    path("approve/", PayApproveView.as_view()),
    path("history/", PaymentHistoryAPIView.as_view()),  # API endpoint
]
