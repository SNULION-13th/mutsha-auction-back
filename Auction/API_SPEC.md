# 경매 히스토리 API 명세서

## 1. 내가 등록한 경매 히스토리 조회

### 기본 정보
- **Endpoint**: `GET /auction/my-auctions/`
- **설명**: 로그인한 사용자가 판매자로 등록한 모든 경매 목록을 조회합니다.
- **인증**: Required (쿠키 기반 자동 인증)

### TypeScript 타입 정의

```typescript
export type MyAuctionItem = {
  auction_id: number;
  title: string;
  current_price: number;
  start_price: number;
  end_time: string;
  status: "active" | "ended" | "cancelled";
  image_url: string | null;
  image_file: string | null;
  image_file_url: string | null;
};
```

### Request 예시

```typescript
import { api } from "./axios";

export async function getMyAuctions(): Promise<MyAuctionItem[]> {
  try {
    const response = await api.get<MyAuctionItem[]>("/auction/my-auctions/");
    if (response.status === 200) {
      return response.data;
    }
    return [];
  } catch (e: unknown) {
    if (isAxiosError(e)) {
      console.error(
        "getMyAuctions error:",
        e.response?.status,
        e.response?.data,
      );
    } else {
      console.error("getMyAuctions unknown error:", e);
    }
    return [];
  }
}
```

### Response 예시

#### Success (200 OK)
```json
[
  {
    "auction_id": 1,
    "title": "아이폰 15 Pro",
    "current_price": 850000,
    "start_price": 500000,
    "end_time": "2025-10-20T15:00:00Z",
    "status": "active",
    "image_url": "https://example.com/image.jpg",
    "image_file": "/media/auction_images/iphone.jpg",
    "image_file_url": "http://localhost:8000/media/auction_images/iphone.jpg"
  },
  {
    "auction_id": 2,
    "title": "맥북 프로",
    "current_price": 1200000,
    "start_price": 800000,
    "end_time": "2025-10-18T20:00:00Z",
    "status": "ended",
    "image_url": null,
    "image_file": "/media/auction_images/macbook.jpg",
    "image_file_url": "http://localhost:8000/media/auction_images/macbook.jpg"
  }
]
```

#### Error (401 Unauthorized)
```json
{
  "detail": "please signin"
}
```

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| auction_id | number | 경매 고유 ID |
| title | string | 경매 제목 |
| current_price | number | 현재 최고 입찰가 |
| start_price | number | 시작가 |
| end_time | string | 경매 종료 시간 (ISO 8601 형식) |
| status | string | 경매 상태 (`active`, `ended`, `cancelled`) |
| image_url | string \| null | 외부 이미지 URL |
| image_file | string \| null | 업로드된 이미지 파일 경로 |
| image_file_url | string \| null | 이미지 파일의 전체 URL |

---

## 2. 내가 입찰한 경매 히스토리 조회

### 기본 정보
- **Endpoint**: `GET /auction/my-bids/`
- **설명**: 로그인한 사용자가 입찰한 모든 경매 목록과 입찰 정보를 조회합니다.
- **인증**: Required (쿠키 기반 자동 인증)

### TypeScript 타입 정의

```typescript
export type MyBidItem = {
  auction_id: number;
  title: string;
  status: "active" | "ended";
  current_price: number;
  my_bid: number;
  end_time: string;
  is_winner: boolean;
  image_url: string | null;
  image_file: string | null;
  image_file_url: string | null;
};
```

### Request 예시

```typescript
import { api } from "./axios";

export async function getMyBids(): Promise<MyBidItem[]> {
  try {
    const response = await api.get<MyBidItem[]>("/auction/my-bids/");
    if (response.status === 200) {
      return response.data;
    }
    return [];
  } catch (e: unknown) {
    if (isAxiosError(e)) {
      console.error(
        "getMyBids error:",
        e.response?.status,
        e.response?.data,
      );
    } else {
      console.error("getMyBids unknown error:", e);
    }
    return [];
  }
}
```

### Response 예시

#### Success (200 OK)
```json
[
  {
    "auction_id": 3,
    "title": "갤럭시 S24 Ultra",
    "status": "active",
    "current_price": 950000,
    "my_bid": 920000,
    "end_time": "2025-10-21T18:00:00Z",
    "is_winner": false,
    "image_url": null,
    "image_file": "/media/auction_images/galaxy.jpg",
    "image_file_url": "http://localhost:8000/media/auction_images/galaxy.jpg"
  },
  {
    "auction_id": 4,
    "title": "에어팟 프로 2",
    "status": "ended",
    "current_price": 180000,
    "my_bid": 180000,
    "end_time": "2025-10-13T12:00:00Z",
    "is_winner": true,
    "image_url": "https://example.com/airpods.jpg",
    "image_file": null,
    "image_file_url": null
  },
  {
    "auction_id": 5,
    "title": "애플워치",
    "status": "ended",
    "current_price": 350000,
    "my_bid": 320000,
    "end_time": "2025-10-12T16:00:00Z",
    "is_winner": false,
    "image_url": null,
    "image_file": "/media/auction_images/watch.jpg",
    "image_file_url": "http://localhost:8000/media/auction_images/watch.jpg"
  }
]
```

#### Error (401 Unauthorized)
```json
{
  "detail": "please signin"
}
```

### Response Fields
| Field | Type | Description |
|-------|------|-------------|
| auction_id | number | 경매 고유 ID |
| title | string | 경매 제목 |
| status | string | 경매 상태 (`active`, `ended`) |
| current_price | number | 현재 최고 입찰가 |
| my_bid | number | 사용자의 최고 입찰가 (입찰 내역 중 가장 높은 금액) |
| end_time | string | 경매 종료 시간 (ISO 8601 형식) |
| is_winner | boolean | 낙찰 여부 (경매가 종료되고 사용자가 최고 입찰자인 경우 `true`) |
| image_url | string \| null | 외부 이미지 URL |
| image_file | string \| null | 업로드된 이미지 파일 경로 |
| image_file_url | string \| null | 이미지 파일의 전체 URL |

---

## 실전 사용 예시

### 컴포넌트에서 사용하기

```tsx
// src/pages/HistoryPage.tsx
import { useEffect, useState } from "react";
import { getMyAuctions, getMyBids, MyAuctionItem, MyBidItem } from "@/apis/api";

export default function HistoryPage() {
  const [myAuctions, setMyAuctions] = useState<MyAuctionItem[]>([]);
  const [myBids, setMyBids] = useState<MyBidItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      
      // 병렬로 두 API 호출
      const [auctionsData, bidsData] = await Promise.all([
        getMyAuctions(),
        getMyBids(),
      ]);
      
      setMyAuctions(auctionsData);
      setMyBids(bidsData);
      setLoading(false);
    };

    fetchHistory();
  }, []);

  // 낙찰된 경매만 필터링
  const wonAuctions = myBids.filter((auction) => auction.is_winner);

  // 진행 중인 입찰만 필터링
  const activeBids = myBids.filter((auction) => auction.status === "active");

  if (loading) return <div>로딩 중...</div>;

  return (
    <div>
      <section>
        <h2>내가 등록한 경매 ({myAuctions.length})</h2>
        {myAuctions.map((auction) => (
          <div key={auction.auction_id}>
            <h3>{auction.title}</h3>
            <p>현재가: {auction.current_price.toLocaleString()}원</p>
            <p>상태: {auction.status}</p>
          </div>
        ))}
      </section>

      <section>
        <h2>낙찰받은 경매 ({wonAuctions.length})</h2>
        {wonAuctions.map((auction) => (
          <div key={auction.auction_id}>
            <h3>{auction.title}</h3>
            <p>낙찰가: {auction.current_price.toLocaleString()}원</p>
            <p>내 입찰가: {auction.my_bid.toLocaleString()}원</p>
          </div>
        ))}
      </section>

      <section>
        <h2>입찰 중인 경매 ({activeBids.length})</h2>
        {activeBids.map((auction) => (
          <div key={auction.auction_id}>
            <h3>{auction.title}</h3>
            <p>현재 최고가: {auction.current_price.toLocaleString()}원</p>
            <p>내 입찰가: {auction.my_bid.toLocaleString()}원</p>
            <p>
              {auction.my_bid >= auction.current_price 
                ? "🎉 현재 최고 입찰자입니다!" 
                : "다른 사람이 더 높은 가격으로 입찰했습니다."}
            </p>
          </div>
        ))}
      </section>
    </div>
  );
}
```

### 페이지 새로고침 시 데이터 불러오기

```tsx
// src/pages/AuctionRoomPage.tsx
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getAuctionDetail, getMyBids } from "@/apis/api";

export default function AuctionRoomPage() {
  const { auctionId } = useParams<{ auctionId: string }>();
  const [myBidAmount, setMyBidAmount] = useState<number>(0);

  useEffect(() => {
    const loadMyBid = async () => {
      if (!auctionId) return;

      // 내 입찰 히스토리에서 현재 경매의 입찰가 찾기
      const myBids = await getMyBids();
      const currentAuctionBid = myBids.find(
        (bid) => bid.auction_id === Number(auctionId)
      );

      if (currentAuctionBid) {
        setMyBidAmount(currentAuctionBid.my_bid);
        console.log("내 이전 입찰가:", currentAuctionBid.my_bid);
      }
    };

    loadMyBid();
  }, [auctionId]);

  return (
    <div>
      {myBidAmount > 0 && (
        <div className="my-bid-info">
          <p>내가 입찰한 금액: {myBidAmount.toLocaleString()}원</p>
        </div>
      )}
      {/* 나머지 경매 상세 페이지 내용 */}
    </div>
  );
}
```