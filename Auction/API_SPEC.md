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

---

## 🧪 테스트 데이터 생성

### 1. 자동 테스트 데이터 생성 명령어

프로젝트에서 API를 쉽게 테스트할 수 있도록 샘플 데이터를 자동으로 생성하는 Django management command를 제공합니다.

```bash
# 백엔드 디렉토리에서 실행
cd mutsha-auction-back-professor
python manage.py create_test_data
```

### 2. 생성되는 데이터

#### 👤 테스트 유저 (3명)

| 유저명 | 비밀번호 | 역할 |
|--------|---------|------|
| `test_seller` | `test1234` | 판매자 (경매 등록) |
| `test_bidder` | `test1234` | 입찰자 (경매 입찰) |
| `test_competitor` | `test1234` | 경쟁 입찰자 |

#### 🏪 내가 등록한 경매 (test_seller 계정)

로그인: `test_seller` / `test1234`

| 제목 | 시작가 | 현재가 | 상태 | 설명 |
|-----|--------|--------|------|------|
| [판매] 아이폰 15 Pro | 500,000원 | 850,000원 | 진행중 | 2일 후 종료 |
| [판매] 맥북 프로 M3 | 1,000,000원 | 1,200,000원 | 진행중 | 5일 후 종료 |
| [판매] 에어팟 프로 2 | 150,000원 | 200,000원 | 종료 | 낙찰자: test_competitor |

**API 테스트:**
```bash
# test_seller로 로그인 후
GET /api/auction/my-auctions/

# 응답: 3개의 경매 (진행중 2개, 종료 1개)
```

#### 💰 내가 입찰한 경매 (test_bidder 계정)

로그인: `test_bidder` / `test1234`

| 제목 | 현재가 | 내 입찰가 | 상태 | is_winner | 설명 |
|-----|--------|-----------|------|-----------|------|
| 갤럭시 S24 Ultra | 950,000원 | 950,000원 | 진행중 | false | 현재 최고 입찰자 ✅ |
| 애플워치 울트라 2 | 700,000원 | 600,000원 | 진행중 | false | 다른 사람이 더 높게 입찰 |
| 아이패드 프로 11인치 | 750,000원 | 750,000원 | 종료 | **true** | 낙찰 성공! 🎉 |
| 닌텐도 스위치 OLED | 320,000원 | 280,000원 | 종료 | false | 낙찰 실패 |

**API 테스트:**
```bash
# test_bidder로 로그인 후
GET /api/auction/my-bids/

# 응답: 4개의 경매
# - 진행중 2개 (최고가 1개, 뒤처진 1개)
# - 종료 2개 (낙찰 성공 1개, 실패 1개)
```

### 4. 명령어 실행 결과

```bash
$ python manage.py create_test_data

테스트 데이터 생성 시작...
1. 유저 생성 중...
  ✓ 판매자 생성: test_seller
  ✓ 입찰자 생성: test_bidder
  ✓ 경쟁자 생성: test_competitor

2. 내가 등록한 경매 생성 중...
  ✓ 경매 생성: [판매] 아이폰 15 Pro (진행중)
  ✓ 경매 생성: [판매] 맥북 프로 M3 (진행중)
  ✓ 경매 생성: [판매] 에어팟 프로 2 (종료됨, 낙찰자: test_competitor)

3. 다른 사람의 경매 생성 중...
  ✓ 경매 생성: 갤럭시 S24 Ultra
  ✓ 경매 생성: 애플워치 울트라 2
  ✓ 경매 생성: 아이패드 프로 11인치 (종료됨, 낙찰자: test_bidder)
  ✓ 경매 생성: 닌텐도 스위치 OLED (종료됨, 낙찰자: test_competitor)

4. 입찰 내역 생성 중...
  ✓ 입찰: 갤럭시 S24 Ultra - 900,000원
  ✓ 입찰: 갤럭시 S24 Ultra - 950,000원 (현재 최고가)
  ✓ 입찰: 애플워치 울트라 2 - 600,000원
  ✓ 입찰: 애플워치 울트라 2 - 700,000원 (경쟁자)
  ✓ 입찰: 아이패드 프로 11인치 - 700,000원
  ✓ 입찰: 아이패드 프로 11인치 - 750,000원 (낙찰가)
  ✓ 입찰: 닌텐도 스위치 OLED - 280,000원
  ✓ 입찰: 닌텐도 스위치 OLED - 320,000원 (경쟁자 낙찰)
  ✓ 입찰: [판매] 아이폰 15 Pro - 850,000원 (내 경매에 입찰)
  ✓ 입찰: [판매] 맥북 프로 M3 - 1,200,000원 (내 경매에 입찰)
  ✓ 입찰: [판매] 에어팟 프로 2 - 200,000원 (내 경매 낙찰)

============================================================
✅ 테스트 데이터 생성 완료!
============================================================

📊 생성된 데이터 요약:

👤 유저:
  - 판매자 (내가 등록): test_seller / test1234
  - 입찰자 (내가 입찰): test_bidder / test1234
  - 경쟁자: test_competitor / test1234

🏪 내가 등록한 경매 (test_seller로 로그인):
  - [판매] 아이폰 15 Pro (진행중)
  - [판매] 맥북 프로 M3 (진행중)
  - [판매] 에어팟 프로 2 (종료됨)

💰 내가 입찰한 경매 (test_bidder로 로그인):
  - 갤럭시 S24 Ultra (진행중, 최고가 입찰자)
  - 애플워치 울트라 2 (진행중, 다른 사람이 더 높게 입찰)
  - 아이패드 프로 11인치 (종료됨, 낙찰 성공 ✓)
  - 닌텐도 스위치 OLED (종료됨, 낙찰 실패 ✗)

🧪 테스트 방법:
  1. test_seller로 로그인 → GET /auction/my-auctions/
     → 3개의 경매 (진행중 2개, 종료 1개)
  2. test_bidder로 로그인 → GET /auction/my-bids/
     → 4개의 경매 (진행중 2개, 낙찰 1개, 낙찰 실패 1개)
```

### 5. 데이터 재생성

데이터를 다시 생성하려면 명령어를 다시 실행하면 됩니다. 이미 존재하는 데이터는 스킵되므로 안전합니다.

```bash
# 기존 테스트 데이터 삭제 (선택사항)
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username__startswith='test_').delete()
>>> from Auction.models import Auction, Bid
>>> Auction.objects.all().delete()
>>> Bid.objects.all().delete()
>>> exit()

# 새로 생성
python manage.py create_test_data
```

