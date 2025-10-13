# 경매 히스토리 API 명세서

> 이 문서는 프론트엔드의 axios 설정을 기반으로 작성되었습니다.

## 📌 기본 설정

### Axios 인스턴스
```typescript
// src/apis/axios.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const api: AxiosInstance = axios.create({
  baseURL: `${BASE_URL}/api`,
  headers: { "Content-Type": "application/json" },
  withCredentials: true, // 쿠키 자동 포함
});
```

### 인증 방식
- **쿠키 기반 인증**: `access_token`, `refresh_token`이 쿠키에 저장되어 자동으로 전송됩니다.
- **Authorization 헤더 불필요**: `withCredentials: true` 설정으로 쿠키가 자동 포함됩니다.
- **자동 토큰 갱신**: 401 에러 발생 시 interceptor가 자동으로 refresh token을 사용해 재시도합니다.

---

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

### React Query 사용 시

```tsx
// src/apis/queries.ts
import { useQuery } from "@tanstack/react-query";
import { getMyAuctions, getMyBids } from "./api";

export function useMyAuctions() {
  return useQuery({
    queryKey: ["myAuctions"],
    queryFn: getMyAuctions,
    staleTime: 1000 * 60 * 5, // 5분
  });
}

export function useMyBids() {
  return useQuery({
    queryKey: ["myBids"],
    queryFn: getMyBids,
    staleTime: 1000 * 60 * 5, // 5분
  });
}

// 컴포넌트에서 사용
function HistoryPage() {
  const { data: myAuctions, isLoading: auctionsLoading } = useMyAuctions();
  const { data: myBids, isLoading: bidsLoading } = useMyBids();

  if (auctionsLoading || bidsLoading) return <div>로딩 중...</div>;

  return (
    <div>
      {/* UI 렌더링 */}
    </div>
  );
}
```

---

## 주요 특징

### 1. 쿠키 기반 인증
- `withCredentials: true` 설정으로 모든 요청에 쿠키 자동 포함
- 별도의 Authorization 헤더 설정 불필요
- `access_token`과 `refresh_token`이 쿠키로 관리됨

### 2. 자동 토큰 갱신
- 401 에러 발생 시 axios interceptor가 자동으로 refresh token으로 재시도
- 개발자가 직접 토큰 갱신 로직을 작성할 필요 없음

### 3. 입찰 정보 영구 저장
- 모든 입찰은 데이터베이스에 저장됨
- 페이지 새로고침 후에도 내 입찰가 확인 가능
- 각 사용자의 최고 입찰가를 `my_bid`로 제공

### 4. 낙찰자 자동 설정
- 경매 종료 시 자동으로 최고 입찰자를 `winner`로 설정
- `is_winner` 필드로 낙찰 여부 확인 가능

---

## API 테스트

### 개발 환경에서 테스트

```bash
# .env.local 설정
VITE_API_BASE_URL=http://localhost:8000
```

```typescript
// 콘솔에서 테스트
const testMyAuctions = async () => {
  const data = await getMyAuctions();
  console.log("내가 등록한 경매:", data);
};

const testMyBids = async () => {
  const data = await getMyBids();
  console.log("내가 입찰한 경매:", data);
  
  // 낙찰된 경매만
  const won = data.filter(a => a.is_winner);
  console.log("낙찰받은 경매:", won);
  
  // 진행 중인 경매만
  const active = data.filter(a => a.status === "active");
  console.log("입찰 중인 경매:", active);
};

testMyAuctions();
testMyBids();
```

---

## 에러 처리

### 일반적인 에러 처리 패턴

```typescript
export async function getMyAuctions(): Promise<MyAuctionItem[]> {
  try {
    const response = await api.get<MyAuctionItem[]>("/auction/my-auctions/");
    if (response.status === 200) {
      return response.data;
    }
    return [];
  } catch (e: unknown) {
    if (isAxiosError(e)) {
      // 401: 로그인 필요 (interceptor가 자동 처리)
      if (e.response?.status === 401) {
        console.error("로그인이 필요합니다.");
      }
      // 기타 에러
      console.error("API 에러:", e.response?.status, e.response?.data);
    } else {
      console.error("알 수 없는 에러:", e);
    }
    return [];
  }
}
```

### 에러 상태 코드
| Status | Description | 처리 방법 |
|--------|-------------|-----------|
| 200 | 성공 | 데이터 반환 |
| 401 | 인증 필요 | Interceptor가 자동으로 토큰 갱신 시도 |
| 500 | 서버 에러 | 에러 메시지 표시 |

---

## 추가 참고사항

### 정렬 순서
- **내가 등록한 경매**: 생성일 기준 최신순 (`-created_at`)
- **내가 입찰한 경매**: 수정일 기준 최신순 (`-updated_at`)

### 성능 최적화
- 입찰한 경매 조회 시 `distinct()`를 사용하여 중복 제거
- 필요한 데이터만 조회하여 네트워크 비용 최소화

### 보안
- 쿠키는 HttpOnly 설정으로 XSS 공격 방지
- 사용자는 자신의 데이터만 조회 가능
- CORS 설정으로 허용된 도메인에서만 접근 가능
