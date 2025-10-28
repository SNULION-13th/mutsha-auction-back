from django.db import models
from django.utils import timezone

# Create your models here.
from django.contrib.auth.models import User

# Create your models here.
class Payment(models.Model):
    tid=models.CharField(max_length=100)
    partner_order_id=models.CharField(max_length=100)
    partner_user_id=models.CharField(max_length=100)
    point=models.IntegerField(default=0)
    price=models.IntegerField(default=0)
    pay_status=models.CharField(max_length=100, default='ready')
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='pay_buyer', null=True)
    created_at=models.DateTimeField(default=timezone.now)
    
    # 카카오페이 API 응답에서 받은 추가 정보
    item_name=models.CharField(max_length=100, blank=True, null=True)
    payment_method_type=models.CharField(max_length=20, default='CARD')
    approved_at=models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']