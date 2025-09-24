#!/usr/bin/env python
"""
예시 결제 내역 데이터를 생성하는 스크립트
사용법: python manage.py shell < create_sample_payments.py
"""

from django.contrib.auth.models import User
from Payment.models import Payment
from UserProfile.models import UserProfile
from datetime import datetime, timedelta
import random

# 사용자 확인 및 생성
try:
    user = User.objects.get(username='admin')
except User.DoesNotExist:
    print("admin 사용자가 없습니다. 다른 사용자를 사용하거나 admin 사용자를 생성해주세요.")
    # admin 사용자 생성
    user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print("admin 사용자를 생성했습니다.")

# UserProfile 확인 및 생성
try:
    user_profile = UserProfile.objects.get(user=user)
except UserProfile.DoesNotExist:
    user_profile = UserProfile.objects.create(
        user=user,
        nickname='관리자',
        remaining_points=10000,
        is_social_login=False
    )
    print("UserProfile을 생성했습니다.")

# 기존 예시 데이터 삭제 (선택사항)
# Payment.objects.filter(user=user).delete()
# print("기존 예시 데이터를 삭제했습니다.")

# 예시 결제 내역 데이터 생성
sample_payments = [
    {
        'tid': 'T1234567890123456789',
        'partner_order_id': 'order_20241201_001',
        'partner_user_id': 'user_001',
        'point': 1000,
        'price': 1000,
        'pay_status': 'approved',
        'item_name': '1000 포인트',
        'payment_method_type': 'CARD',
        'approved_at': datetime.now() - timedelta(days=1),
        'aid': 'A1234567890123456789',
        'cid': 'TC0ONETIME',
        'sid': 'S1234567890123456789',
        'status': 'DONE',
        'quantity': 1,
        'vat_amount': 91,
        'tax_free_amount': 909,
        'created_at': datetime.now() - timedelta(days=1, hours=2),
        'payload': '{"custom_data": "sample_payment_1"}',
        'card_info': {
            'purchase_corp': '신한카드',
            'purchase_corp_code': '03',
            'issuer_corp': '신한카드',
            'issuer_corp_code': '03',
            'kakaopay_purchase_corp': '신한카드',
            'kakaopay_purchase_corp_code': '03',
            'kakaopay_issuer_corp': '신한카드',
            'kakaopay_issuer_corp_code': '03',
            'bin': '123456',
            'card_type': 'CREDIT',
            'install_month': '00',
            'approved_id': '12345678',
            'card_mid': '1234567890',
            'interest_free_install': 'N',
            'card_item_code': '1234567890'
        }
    },
    {
        'tid': 'T1234567890123456790',
        'partner_order_id': 'order_20241201_002',
        'partner_user_id': 'user_001',
        'point': 5000,
        'price': 5000,
        'pay_status': 'approved',
        'item_name': '5000 포인트',
        'payment_method_type': 'CARD',
        'approved_at': datetime.now() - timedelta(days=3),
        'aid': 'A1234567890123456790',
        'cid': 'TC0ONETIME',
        'sid': 'S1234567890123456790',
        'status': 'DONE',
        'quantity': 1,
        'vat_amount': 455,
        'tax_free_amount': 4545,
        'created_at': datetime.now() - timedelta(days=3, hours=1),
        'payload': '{"custom_data": "sample_payment_2"}',
        'card_info': {
            'purchase_corp': 'KB카드',
            'purchase_corp_code': '01',
            'issuer_corp': 'KB카드',
            'issuer_corp_code': '01',
            'kakaopay_purchase_corp': 'KB카드',
            'kakaopay_purchase_corp_code': '01',
            'kakaopay_issuer_corp': 'KB카드',
            'kakaopay_issuer_corp_code': '01',
            'bin': '654321',
            'card_type': 'CREDIT',
            'install_month': '00',
            'approved_id': '87654321',
            'card_mid': '0987654321',
            'interest_free_install': 'N',
            'card_item_code': '0987654321'
        }
    },
    {
        'tid': 'T1234567890123456791',
        'partner_order_id': 'order_20241201_003',
        'partner_user_id': 'user_001',
        'point': 10000,
        'price': 10000,
        'pay_status': 'approved',
        'item_name': '10000 포인트',
        'payment_method_type': 'MONEY',
        'approved_at': datetime.now() - timedelta(days=7),
        'aid': 'A1234567890123456791',
        'cid': 'TC0ONETIME',
        'sid': 'S1234567890123456791',
        'status': 'DONE',
        'quantity': 1,
        'vat_amount': 0,
        'tax_free_amount': 10000,
        'created_at': datetime.now() - timedelta(days=7, hours=3),
        'payload': '{"custom_data": "sample_payment_3"}',
        'card_info': {}
    },
    {
        'tid': 'T1234567890123456792',
        'partner_order_id': 'order_20241201_004',
        'partner_user_id': 'user_001',
        'point': 2000,
        'price': 2000,
        'pay_status': 'approved',
        'item_name': '2000 포인트',
        'payment_method_type': 'CARD',
        'approved_at': datetime.now() - timedelta(days=10),
        'aid': 'A1234567890123456792',
        'cid': 'TC0ONETIME',
        'sid': 'S1234567890123456792',
        'status': 'DONE',
        'quantity': 1,
        'vat_amount': 182,
        'tax_free_amount': 1818,
        'created_at': datetime.now() - timedelta(days=10, hours=5),
        'payload': '{"custom_data": "sample_payment_4"}',
        'card_info': {
            'purchase_corp': '하나카드',
            'purchase_corp_code': '04',
            'issuer_corp': '하나카드',
            'issuer_corp_code': '04',
            'kakaopay_purchase_corp': '하나카드',
            'kakaopay_purchase_corp_code': '04',
            'kakaopay_issuer_corp': '하나카드',
            'kakaopay_issuer_corp_code': '04',
            'bin': '789012',
            'card_type': 'DEBIT',
            'install_month': '00',
            'approved_id': '11223344',
            'card_mid': '1122334455',
            'interest_free_install': 'N',
            'card_item_code': '1122334455'
        }
    }
]

# 결제 내역 생성
created_payments = []
for payment_data in sample_payments:
    payment = Payment.objects.create(
        user=user,
        **payment_data
    )
    created_payments.append(payment)
    print(f"결제 내역 생성: {payment.item_name} - {payment.price}원 ({payment.payment_method_type})")

print(f"\n총 {len(created_payments)}개의 예시 결제 내역이 생성되었습니다.")
print(f"사용자: {user.username}")
print(f"총 결제 금액: {sum(p.price for p in created_payments)}원")
print(f"총 충전 포인트: {sum(p.point for p in created_payments)}포인트")

# 사용자 포인트 업데이트
user_profile.remaining_points += sum(p.point for p in created_payments)
user_profile.save()
print(f"사용자 포인트 업데이트: {user_profile.remaining_points}포인트")
