from django.urls import path
from .views import PayReadyView, PayApproveView, PayHistoryView ## 추가

app_name = "payment"
urlpatterns = [
    # CBV url path
    path("ready/", PayReadyView.as_view()),
    ### 🔻 이 부분 추가 ###
    path("approve/", PayApproveView.as_view()),
    path("history/", PayHistoryView.as_view()), # history/ 로 요청을 보내면 PayHistoryView에 있는 함수가 실행된다~
]