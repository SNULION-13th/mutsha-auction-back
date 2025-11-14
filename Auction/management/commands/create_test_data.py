from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from Auction.models import Auction, Bid


class Command(BaseCommand):
    help = '경매 히스토리 API 테스트를 위한 샘플 데이터를 생성합니다.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('테스트 데이터 생성 시작...'))

        # 1. 테스트 유저 생성
        self.stdout.write('1. 유저 생성 중...')
        
        # 판매자 유저 (내가 경매를 등록한 사람)
        seller_user, created = User.objects.get_or_create(
            username='test_seller',
            defaults={'password': 'pbkdf2_sha256$720000$testpassword'}
        )
        if created:
            seller_user.set_password('test1234')
            seller_user.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ 판매자 생성: {seller_user.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 판매자 이미 존재: {seller_user.username}'))

        # 입찰자 유저 (내가 입찰한 사람)
        bidder_user, created = User.objects.get_or_create(
            username='test_bidder',
            defaults={'password': 'pbkdf2_sha256$720000$testpassword'}
        )
        if created:
            bidder_user.set_password('test1234')
            bidder_user.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰자 생성: {bidder_user.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 입찰자 이미 존재: {bidder_user.username}'))

        # 경쟁 입찰자 (다른 사람)
        competitor_user, created = User.objects.get_or_create(
            username='test_competitor',
            defaults={'password': 'pbkdf2_sha256$720000$testpassword'}
        )
        if created:
            competitor_user.set_password('test1234')
            competitor_user.save()
            self.stdout.write(self.style.SUCCESS(f'  ✓ 경쟁자 생성: {competitor_user.username}'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 경쟁자 이미 존재: {competitor_user.username}'))

        # 2. 내가 등록한 경매 생성 (판매자 입장)
        self.stdout.write('\n2. 내가 등록한 경매 생성 중...')
        
        # 진행중인 경매 1
        auction1, created = Auction.objects.get_or_create(
            title='[판매] 아이폰 15 Pro',
            seller=seller_user,
            defaults={
                'description': '새 제품입니다. 직거래 가능합니다.',
                'starting_price': 500000,
                'current_price': 850000,
                'status': 'active',
                'end_time': timezone.now() + timedelta(days=2)
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 경매 생성: {auction1.title} (진행중)'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 경매 이미 존재: {auction1.title}'))

        # 진행중인 경매 2
        auction2, created = Auction.objects.get_or_create(
            title='[판매] 맥북 프로 M3',
            seller=seller_user,
            defaults={
                'description': '1년 사용, 거의 새 제품입니다.',
                'starting_price': 1000000,
                'current_price': 1200000,
                'status': 'active',
                'end_time': timezone.now() + timedelta(days=5)
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 경매 생성: {auction2.title} (진행중)'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 경매 이미 존재: {auction2.title}'))

        # 종료된 경매 (낙찰됨)
        auction3, created = Auction.objects.get_or_create(
            title='[판매] 에어팟 프로 2',
            seller=seller_user,
            defaults={
                'description': '미개봉 새 제품입니다.',
                'starting_price': 150000,
                'current_price': 200000,
                'status': 'ended',
                'end_time': timezone.now() - timedelta(days=1),
                'winner': competitor_user  # 경쟁자가 낙찰받음
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 경매 생성: {auction3.title} (종료됨, 낙찰자: {competitor_user.username})'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 경매 이미 존재: {auction3.title}'))

        # 3. 다른 사람이 등록한 경매 생성 (내가 입찰할 경매)
        self.stdout.write('\n3. 다른 사람의 경매 생성 중...')
        
        # 내가 입찰해서 현재 최고가인 경매
        auction4, created = Auction.objects.get_or_create(
            title='갤럭시 S24 Ultra',
            seller=competitor_user,
            defaults={
                'description': '완전 새 제품, 미개봉입니다.',
                'starting_price': 800000,
                'current_price': 950000,
                'status': 'active',
                'end_time': timezone.now() + timedelta(days=3)
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 경매 생성: {auction4.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 경매 이미 존재: {auction4.title}'))

        # 내가 입찰했지만 다른 사람이 더 높은 가격으로 입찰한 경매
        auction5, created = Auction.objects.get_or_create(
            title='애플워치 울트라 2',
            seller=competitor_user,
            defaults={
                'description': '3개월 사용, 상태 좋습니다.',
                'starting_price': 500000,
                'current_price': 700000,
                'status': 'active',
                'end_time': timezone.now() + timedelta(days=1)
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 경매 생성: {auction5.title}'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 경매 이미 존재: {auction5.title}'))

        # 내가 낙찰받은 종료된 경매
        auction6, created = Auction.objects.get_or_create(
            title='아이패드 프로 11인치',
            seller=competitor_user,
            defaults={
                'description': '6개월 사용, 케이스 포함.',
                'starting_price': 600000,
                'current_price': 750000,
                'status': 'ended',
                'end_time': timezone.now() - timedelta(days=2),
                'winner': bidder_user  # 내가 낙찰받음
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 경매 생성: {auction6.title} (종료됨, 낙찰자: {bidder_user.username})'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 경매 이미 존재: {auction6.title}'))

        # 내가 입찰했지만 낙찰받지 못한 종료된 경매
        auction7, created = Auction.objects.get_or_create(
            title='닌텐도 스위치 OLED',
            seller=competitor_user,
            defaults={
                'description': '거의 새 제품, 게임 3개 포함.',
                'starting_price': 250000,
                'current_price': 320000,
                'status': 'ended',
                'end_time': timezone.now() - timedelta(days=3),
                'winner': competitor_user  # 다른 사람이 낙찰받음
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 경매 생성: {auction7.title} (종료됨, 낙찰자: {competitor_user.username})'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠ 경매 이미 존재: {auction7.title}'))

        # 4. 입찰 내역 생성
        self.stdout.write('\n4. 입찰 내역 생성 중...')

        # auction4: 내가 최고가로 입찰
        bid1, created = Bid.objects.get_or_create(
            auction=auction4,
            bidder=bidder_user,
            amount=900000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction4.title} - {bid1.amount:,}원'))

        bid2, created = Bid.objects.get_or_create(
            auction=auction4,
            bidder=bidder_user,
            amount=950000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction4.title} - {bid2.amount:,}원 (현재 최고가)'))

        # auction5: 내가 입찰했지만 다른 사람이 더 높게 입찰
        bid3, created = Bid.objects.get_or_create(
            auction=auction5,
            bidder=bidder_user,
            amount=600000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction5.title} - {bid3.amount:,}원'))

        bid4, created = Bid.objects.get_or_create(
            auction=auction5,
            bidder=competitor_user,
            amount=700000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction5.title} - {bid4.amount:,}원 (경쟁자)'))

        # auction6: 내가 낙찰받은 경매
        bid5, created = Bid.objects.get_or_create(
            auction=auction6,
            bidder=bidder_user,
            amount=700000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction6.title} - {bid5.amount:,}원'))

        bid6, created = Bid.objects.get_or_create(
            auction=auction6,
            bidder=bidder_user,
            amount=750000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction6.title} - {bid6.amount:,}원 (낙찰가)'))

        # auction7: 내가 입찰했지만 낙찰받지 못한 경매
        bid7, created = Bid.objects.get_or_create(
            auction=auction7,
            bidder=bidder_user,
            amount=280000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction7.title} - {bid7.amount:,}원'))

        bid8, created = Bid.objects.get_or_create(
            auction=auction7,
            bidder=competitor_user,
            amount=320000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction7.title} - {bid8.amount:,}원 (경쟁자 낙찰)'))

        # 내가 등록한 경매에 다른 사람의 입찰 추가
        bid9, created = Bid.objects.get_or_create(
            auction=auction1,
            bidder=competitor_user,
            amount=850000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction1.title} - {bid9.amount:,}원 (내 경매에 입찰)'))

        bid10, created = Bid.objects.get_or_create(
            auction=auction2,
            bidder=competitor_user,
            amount=1200000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction2.title} - {bid10.amount:,}원 (내 경매에 입찰)'))

        bid11, created = Bid.objects.get_or_create(
            auction=auction3,
            bidder=competitor_user,
            amount=200000,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ 입찰: {auction3.title} - {bid11.amount:,}원 (내 경매 낙찰)'))

        # 5. 요약 출력
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ 테스트 데이터 생성 완료!'))
        self.stdout.write('='*60)
        self.stdout.write('\n📊 생성된 데이터 요약:')
        self.stdout.write(f'\n👤 유저:')
        self.stdout.write(f'  - 판매자 (내가 등록): test_seller / test1234')
        self.stdout.write(f'  - 입찰자 (내가 입찰): test_bidder / test1234')
        self.stdout.write(f'  - 경쟁자: test_competitor / test1234')
        
        self.stdout.write(f'\n🏪 내가 등록한 경매 (test_seller로 로그인):')
        self.stdout.write(f'  - {auction1.title} (진행중)')
        self.stdout.write(f'  - {auction2.title} (진행중)')
        self.stdout.write(f'  - {auction3.title} (종료됨)')
        
        self.stdout.write(f'\n💰 내가 입찰한 경매 (test_bidder로 로그인):')
        self.stdout.write(f'  - {auction4.title} (진행중, 최고가 입찰자)')
        self.stdout.write(f'  - {auction5.title} (진행중, 다른 사람이 더 높게 입찰)')
        self.stdout.write(f'  - {auction6.title} (종료됨, 낙찰 성공 ✓)')
        self.stdout.write(f'  - {auction7.title} (종료됨, 낙찰 실패 ✗)')
        
        self.stdout.write('\n🧪 테스트 방법:')
        self.stdout.write('  1. test_seller로 로그인 → GET /auction/my-auctions/')
        self.stdout.write('     → 3개의 경매 (진행중 2개, 종료 1개)')
        self.stdout.write('  2. test_bidder로 로그인 → GET /auction/my-bids/')
        self.stdout.write('     → 4개의 경매 (진행중 2개, 낙찰 1개, 낙찰 실패 1개)')
        self.stdout.write('')

