from django.urls import path
from .views import PayReadyView, PayApproveView, OrderTrackView

app_name = "payment"
urlpatterns = [
    # CBV url path
    path("ready/", PayReadyView.as_view()),
    path("approve/", PayApproveView.as_view()),
    path("order/", OrderTrackView.as_view()),
]