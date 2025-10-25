from django.urls import path
from .views import PayReadyView, PayApproveView, PayOrderDetailView, PaymentReceiptView

app_name = "payment"
urlpatterns = [
    # CBV url path
    path("ready/", PayReadyView.as_view()),
    path("approve/", PayApproveView.as_view()),
    path("order/", PayOrderDetailView.as_view()),
    path("receipt/", PaymentReceiptView.as_view()),
]