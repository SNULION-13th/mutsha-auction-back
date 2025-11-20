from django.urls import path
from .views import (
    RecommendedAuctionsView,
    AuctionListView,
    AuctionDetailView,
    AuctionCreateView,
    BidCreateView,
    MyAuctionHistoryView,
    MyBidHistoryView
)

app_name = "Auction"

urlpatterns = [
    # 추천 경매 (오늘의 추천)
    path("recommended/", RecommendedAuctionsView.as_view(), name="recommended_auctions"),
    
    # 경매 목록
    path("", AuctionListView.as_view(), name="auction_list"),
    
    # 경매 상세
    path("<int:auction_id>/", AuctionDetailView.as_view(), name="auction_detail"),
    
    # 경매 생성
    path("create/", AuctionCreateView.as_view(), name="auction_create"),
    
    # 입찰
    path("<int:auction_id>/bid/", BidCreateView.as_view(), name="bid_create"),
    
    # 내가 등록한 경매 히스토리
    path("my-auctions/", MyAuctionHistoryView.as_view(), name="my_auction_history"),
    
    # 내가 입찰한 경매 히스토리
    path("my-bids/", MyBidHistoryView.as_view(), name="my_bid_history"),
]
