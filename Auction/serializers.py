from rest_framework import serializers
from .models import Auction, Bid
from UserProfile.serializers import UserProfileSerializer


class AuctionSerializer(serializers.ModelSerializer):
    """경매 시리얼라이저"""
    seller_nickname = serializers.CharField(source='seller.userprofile.nickname', read_only=True)
    seller_profile_image = serializers.CharField(source='seller.userprofile.profilepic_id', read_only=True)
    time_remaining = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    bid_count = serializers.SerializerMethodField()
    image_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Auction
        fields = [
            'id', 'title', 'description', 'starting_price', 'current_price',
            'image_url', 'image_file', 'image_file_url', 'status', 'start_time', 'end_time',
            'seller', 'seller_nickname', 'seller_profile_image', 'winner',
            'created_at', 'updated_at', 'time_remaining', 'is_active', 'bid_count'
        ]
        read_only_fields = ['current_price', 'created_at', 'updated_at', 'winner']
    
    def get_bid_count(self, obj):
        """입찰 수 반환"""
        return obj.bids.count()
    
    def get_image_file_url(self, obj):
        """이미지 파일의 절대 URL 반환"""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return None


class AuctionListSerializer(serializers.ModelSerializer):
    """경매 목록용 간단한 시리얼라이저"""
    seller_nickname = serializers.CharField(source='seller.userprofile.nickname', read_only=True)
    seller_profile_image = serializers.CharField(source='seller.userprofile.profilepic_id', read_only=True)
    time_remaining = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    bid_count = serializers.SerializerMethodField()
    image_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Auction
        fields = [
            'id', 'title', 'description', 'starting_price', 'current_price',
            'image_url', 'image_file', 'image_file_url', 'status', 'end_time',
            'seller_nickname', 'seller_profile_image',
            'time_remaining', 'is_active', 'bid_count'
        ]
    
    def get_bid_count(self, obj):
        """입찰 수 반환"""
        return obj.bids.count()
    
    def get_image_file_url(self, obj):
        """이미지 파일의 절대 URL 반환"""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return None


class BidSerializer(serializers.ModelSerializer):
    """입찰 시리얼라이저"""
    bidder_nickname = serializers.CharField(source='bidder.userprofile.nickname', read_only=True)
    
    class Meta:
        model = Bid
        fields = ['id', 'auction', 'bidder', 'bidder_nickname', 'amount', 'bid_time']
        read_only_fields = ['bidder', 'bid_time']
    
    def validate_amount(self, value):
        """입찰가 검증"""
        auction = self.context.get('auction')
        if auction and value <= auction.current_price:
            raise serializers.ValidationError("현재가보다 높은 금액을 입찰해야 합니다.")
        return value


class AuctionCreateSerializer(serializers.ModelSerializer):
    """경매 생성용 시리얼라이저"""
    
    class Meta:
        model = Auction
        fields = [
            'title', 'description', 'starting_price', 'image_url', 'image_file', 'end_time'
        ]
    
    def validate_end_time(self, value):
        """종료 시간 검증"""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("종료 시간은 현재 시간보다 늦어야 합니다.")
        return value
