from django.contrib import admin
from .models import Auction, Bid


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'starting_price', 'current_price', 'status', 'start_time', 'end_time']
    list_filter = ['status', 'start_time', 'end_time']
    search_fields = ['title', 'description', 'seller__username']
    readonly_fields = ['created_at', 'updated_at', 'current_price']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'description', 'seller')
        }),
        ('경매 정보', {
            'fields': ('starting_price', 'current_price', 'status', 'start_time', 'end_time')
        }),
        ('이미지', {
            'fields': ('image_url', 'image_file')
        }),
        ('결과', {
            'fields': ('winner',)
        }),
        ('메타데이터', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['auction', 'bidder', 'amount', 'bid_time']
    list_filter = ['bid_time', 'auction__status']
    search_fields = ['auction__title', 'bidder__username']
    readonly_fields = ['bid_time']