from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Payment

class PayReadyRequestSerializer(serializers.Serializer):
  partner_order_id = serializers.CharField()
  partner_user_id = serializers.CharField()
  item_name = serializers.CharField()
  total_amount = serializers.IntegerField()

class PayApproveRequestSerializer(serializers.Serializer):
  pg_token = serializers.CharField()
  tid = serializers.CharField()

class PayReadyResponseSerializer(serializers.Serializer):
  tid = serializers.CharField()
  next_redirect_app_url = serializers.CharField()
  next_redirect_mobile_url = serializers.CharField()
  next_redirect_pc_url = serializers.CharField()
  android_app_scheme = serializers.CharField()
  ios_app_scheme = serializers.CharField()
  created_at = serializers.DateTimeField()

class PayApproveResponseSerializer(serializers.Serializer):
  aid = serializers.CharField()
  tid = serializers.CharField()
  cid = serializers.CharField()
  sid = serializers.CharField()
  status = serializers.CharField()
  partner_order_id = serializers.CharField()
  partner_user_id = serializers.CharField()
  payment_method_type = serializers.CharField()
  amount = serializers.IntegerField()
  card_info = serializers.CharField()
  item_name = serializers.CharField()
  item_code = serializers.CharField()
  quantity = serializers.IntegerField()
  created_at = serializers.DateTimeField()
  approved_at = serializers.DateTimeField()
  payload = serializers.CharField()

class PaymentHistorySerializer(serializers.ModelSerializer):
    # 요구사항 1: 상품 이름 (item_name)
    # Payment 모델의 'point' 필드를 사용하여 'X 포인트 충전' 형태로 변환합니다.
    item_name = serializers.SerializerMethodField() 
    
    # 요구사항 2: 결제 금액 (amount)
    # Payment 모델의 'price' 필드를 'amount'라는 이름으로 응답합니다.
    amount = serializers.IntegerField(source='price') 
    
    # 요구사항 3: 결제 수단 (payment_method_type)
    payment_method_type = serializers.CharField()
    
    # 요구사항 4: 결제 승인 시간 (approved_at)
    approved_at = serializers.DateTimeField() 
    
    class Meta:
        model = Payment # Payment 모델 사용
        fields = (
            'id',
            'item_name',
            'amount',
            'payment_method_type',
            'approved_at',
            'pay_status',
        )

    def get_item_name(self, obj: Payment):
        """충전된 포인트 금액을 상품 이름으로 생성"""
        # item_name이 ready 시점에 point 값으로 들어갔다는 가정하에 사용
        return f"{obj.point} 포인트 충전"
        
    def to_representation(self, instance):
        """카카오페이 수단 타입 한글화"""
        data = super().to_representation(instance)
        
        # 카카오페이 응답 값 (CARD, MONEY)을 한글로 변경
        method_map = {
            'CARD': '카드',
            'MONEY': '카카오머니',
        }
        # 한글화 매핑된 값을 응답 데이터에 적용합니다.
        data['payment_method_type'] = method_map.get(
            data['payment_method_type'], 
            data['payment_method_type']
        )
        return data