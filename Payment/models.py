from django.db import models

# Create your models here.
from django.contrib.auth.models import User

# Create your models here.
class Payment(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='pay_buyer', null=True)
    tid=models.CharField(max_length=100)
    partner_order_id=models.CharField(max_length=100)
    partner_user_id=models.CharField(max_length=100)
    point=models.IntegerField(default=0)
    price=models.IntegerField(default=0, null=True, blank=True)
    pay_status=models.CharField(max_length=100, default='ready')

    # 주문 조회
    item_name=models.CharField(max_length=100, null=True, blank=True)
    payment_method_type=models.CharField(max_length=100, null=True, blank=True)
    approved_at=models.DateTimeField(null=True, blank=True)