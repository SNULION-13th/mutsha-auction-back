# Order/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("detail/", views.payment_detail_api, name="order_payment_detail"),
]
