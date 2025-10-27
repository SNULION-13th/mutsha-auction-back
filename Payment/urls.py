from django.urls import path
from .views import PayReadyView, PayApproveView, PaySyncOrderView, PayOrderListView

app_name = "payment"
urlpatterns = [
    # CBV url path
    path("ready/", PayReadyView.as_view()),
    path("approve/", PayApproveView.as_view()),
    path("sync/", PaySyncOrderView.as_view()),     # 실시간 동기화
    path("list/", PayOrderListView.as_view()),     # 저장된 리스트 불러오기
]