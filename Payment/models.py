from django.db import models

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
    
    item_name = models.CharField(max_length=255, null=True, blank=True)               # 상품 이름
    amount = models.IntegerField(default=0)                                           # 결제 금액 (총액)
    payment_method_type = models.CharField(max_length=50, null=True, blank=True)      # 결제 수단 (CARD 등)
    approved_at = models.DateTimeField(null=True, blank=True)                         # 결제 승인 시각

    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.item_name or self.tid}"
