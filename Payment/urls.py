from django.urls import path
from .views import PayReadyView, PayApproveView, PaymentHistoryView, PaymentHistoryView

app_name = "payment"
urlpatterns = [
    # CBV url path
    path("ready/", PayReadyView.as_view()),
    path("approve/", PayApproveView.as_view()),
    path("history/", PaymentHistoryView.as_view()),
    path("user-history/", PaymentHistoryView.as_view()),
]