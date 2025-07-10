# V-Exchange 매칭 엔진 아키텍처

## 🏗️ 전체 시스템 아키텍처

```mermaid
graph TB
    subgraph "Client Layer"
        WebClient[Web Client]
        WSClient[WebSocket Client]
    end
    
    subgraph "API Layer"
        FastAPI[FastAPI Server]
        REST[REST API]
        WS[WebSocket API]
    end
    
    subgraph "Business Logic Layer"
        OrderService[Order Service]
        MatchingEngine[Matching Engine]
        OrderBook[Order Book]
        TradeService[Trade Service]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL)]
        OrderTable[Orders Table]
        TradeTable[Trades Table]
        LogTable[Logs Table]
    end
    
    subgraph "Real-time Layer"
        WSManager[WebSocket Manager]
        Broadcaster[Event Broadcaster]
    end
    
    WebClient --> REST
    WSClient --> WS
    REST --> OrderService
    WS --> WSManager
    OrderService --> MatchingEngine
    MatchingEngine --> OrderBook
    MatchingEngine --> TradeService
    OrderBook --> PostgreSQL
    TradeService --> PostgreSQL
    MatchingEngine --> WSManager
    WSManager --> Broadcaster
    Broadcaster --> WSClient
```

## 🔄 주문 처리 흐름도

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant OrderService
    participant MatchingEngine
    participant OrderBook
    participant TradeService
    participant DB
    participant WSManager
    
    Client->>API: POST /orders (Limit/Market/IOC)
    API->>OrderService: Create Order
    OrderService->>MatchingEngine: Process Order
    
    alt Limit Order
        MatchingEngine->>OrderBook: Add to Order Book
        OrderBook->>DB: Save Order
        MatchingEngine->>TradeService: Check for Matches
        TradeService->>DB: Create Trade Log
        TradeService->>OrderBook: Update Order Book
    else Market Order
        MatchingEngine->>OrderBook: Immediate Matching
        OrderBook->>TradeService: Execute Trades
        TradeService->>DB: Create Trade Logs
    else IOC Order
        MatchingEngine->>OrderBook: Immediate Matching
        OrderBook->>TradeService: Execute Trades
        TradeService->>DB: Create Trade Logs
        Note over OrderBook: Cancel Remaining
    end
    
    MatchingEngine->>WSManager: Broadcast Updates
    WSManager->>Client: WebSocket Updates
```

## 📊 데이터 모델 관계

```mermaid
erDiagram
    ORDERS {
        uuid id PK
        string symbol
        string side
        string order_type
        decimal price
        decimal quantity
        decimal filled_quantity
        string status
        timestamp created_at
        timestamp updated_at
    }
    
    TRADES {
        uuid id PK
        uuid buy_order_id FK
        uuid sell_order_id FK
        decimal price
        decimal quantity
        timestamp executed_at
    }
    
    ORDER_BOOK {
        string symbol
        decimal price
        decimal total_quantity
        int order_count
        timestamp last_updated
    }
    
    ORDERS ||--o{ TRADES : "generates"
    ORDERS ||--o{ ORDER_BOOK : "updates"
```

## 🎯 핵심 컴포넌트

### 1. **Matching Engine (매칭 엔진)**
- Price-Time Priority 알고리즘
- Market/Limit/IOC 주문 지원
- 실시간 매칭 처리

### 2. **Order Book (오더북)**
- 메모리 기반 고성능 구조
- Price-Time Priority 정렬
- 실시간 업데이트

### 3. **Trade Service (체결 서비스)**
- 매칭 결과 처리
- Trade Log 생성
- 잔고 업데이트 (추후)

### 4. **WebSocket Manager**
- 실시간 오더북 브로드캐스트
- 체결 내역 실시간 전송
- 클라이언트 연결 관리

### 5. **Database Layer**
- PostgreSQL 기반 영속화
- 주문/체결/로그 저장
- 서버 재시작 시 복구

## 🚀 성능 최적화 포인트

1. **메모리 기반 오더북**: 빠른 매칭을 위한 인메모리 처리
2. **비동기 처리**: FastAPI의 비동기 특성 활용
3. **배치 처리**: 대량 주문 처리 시 배치화
4. **인덱싱**: PostgreSQL 인덱스 최적화
5. **캐싱**: Redis 도입 고려 (추후)

## 🔧 확장 계획

### Phase 1: 기본 매칭 엔진
- [x] 프로젝트 구조 설정
- [ ] 기본 모델 설계
- [ ] 오더북 구현
- [ ] 매칭 엔진 구현
- [ ] REST API 구현

### Phase 2: 실시간 기능
- [ ] WebSocket 구현
- [ ] 실시간 오더북 브로드캐스트
- [ ] 실시간 체결 내역

### Phase 3: 고급 기능
- [ ] 계좌/잔고 관리
- [ ] 위험 관리
- [ ] 멀티 마켓 지원

### Phase 4: 운영 기능
- [ ] 모니터링/로깅
- [ ] 성능 최적화
- [ ] 보안 강화 