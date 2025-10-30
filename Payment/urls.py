from django.urls import path
from .views import PayReadyView, PayApproveView ## 추가

app_name = "payment"
urlpatterns = [
    # CBV url path
    path("ready/", PayReadyView.as_view()),
    ### 🔻 이 부분 추가 ###
    path("approve/", PayApproveView.as_view()),
]