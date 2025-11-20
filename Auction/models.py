from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Auction(models.Model):
    title = models.CharField(max_length=200, verbose_name="경매 제목")
    description = models.TextField(verbose_name="경매 설명")
    starting_price = models.PositiveIntegerField(verbose_name="시작가")
    current_price = models.PositiveIntegerField(verbose_name="현재가", default=0)
    image_url = models.URLField(verbose_name="이미지 URL", blank=True, null=True)
    image_file = models.ImageField(upload_to='auction_images/', verbose_name="이미지 파일", blank=True, null=True)
    
    # 경매 상태
    STATUS_CHOICES = [
        ('active', '진행중'),
        ('ended', '종료'),
        ('cancelled', '취소'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="경매 상태")
    
    # 시간 관련
    start_time = models.DateTimeField(default=timezone.now, verbose_name="시작 시간")
    end_time = models.DateTimeField(verbose_name="종료 시간")
    
    # 관계
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions_sold', verbose_name="판매자")
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctions_won', verbose_name="낙찰자")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    
    class Meta:
        verbose_name = "경매"
        verbose_name_plural = "경매들"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.seller.username}"
    
    @property
    def is_active(self):
        """경매가 진행중인지 확인"""
        return self.status == 'active' and timezone.now() < self.end_time
    
    @property
    def time_remaining(self):
        """남은 시간 계산"""
        if self.is_active:
            return self.end_time - timezone.now()
        return None


class Bid(models.Model):
    """입찰 모델"""
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids', verbose_name="경매")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids', verbose_name="입찰자")
    amount = models.PositiveIntegerField(verbose_name="입찰가")
    bid_time = models.DateTimeField(auto_now_add=True, verbose_name="입찰 시간")
    
    class Meta:
        verbose_name = "입찰"
        verbose_name_plural = "입찰들"
        ordering = ['-bid_time']
    
    def __str__(self):
        return f"{self.auction.title} - {self.bidder.username}: {self.amount}원"
    
    def save(self, *args, **kwargs):
        """입찰 저장 시 경매의 current_price 업데이트"""
        super().save(*args, **kwargs)