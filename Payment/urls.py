from django.urls import path
from .views import PayApproveView, PayReadyView, PayDetailView

app_name = "payment"
urlpatterns = [
    # CBV url path
    path("ready/", PayReadyView.as_view()),
    path("approve/", PayApproveView.as_view()),
    path("detail/", PayDetailView.as_view()),
]