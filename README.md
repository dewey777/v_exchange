# V-Exchange 매칭 엔진

바이낸스 수준의 고성능 매칭 엔진 (단일 마켓)

## 🎯 목표

- **오더북 (Order Book)**: 가격 우선, 시간 우선 정렬
- **매칭 알고리즘**: Price-Time Priority
- **주문 타입**: Market / Limit / IOC 지원
- **실시간 처리**: WebSocket 기반 실시간 오더북 출력
- **확장성**: 추후 계좌/잔고/위험 관리 등 연동

## 🏗️ 아키텍처

자세한 아키텍처는 [ARCHITECTURE.md](./ARCHITECTURE.md)를 참조하세요.

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 데이터베이스 설정

```bash
# PostgreSQL 설치 및 데이터베이스 생성
createdb v_exchange

# 환경변수 설정
export DATABASE_URL="postgresql+asyncpg://username:password@localhost/v_exchange"
```

### 3. 애플리케이션 실행

```bash
# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 프로젝트 구조

```
v_exchange/
├── app/
│   ├── api/              # API 엔드포인트
│   ├── core/             # 핵심 로직 (매칭 엔진, 오더북)
│   ├── models/           # SQLAlchemy 모델
│   ├── schemas/          # Pydantic 스키마
│   ├── services/         # 비즈니스 로직
│   ├── db/               # 데이터베이스 설정
│   ├── ws/               # WebSocket 핸들러
│   └── main.py           # FastAPI 진입점
├── tests/                # 테스트 파일
├── requirements.txt       # 의존성
├── ARCHITECTURE.md       # 아키텍처 문서
└── README.md
```

## 🔧 개발 단계

### Phase 1: 기본 매칭 엔진 ✅
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

## 🧪 테스트

```bash
# 테스트 실행
pytest

# 커버리지 포함 테스트
pytest --cov=app
```

## 📊 API 엔드포인트

### 주문 관리
- `POST /orders` - 주문 생성
- `GET /orders/{order_id}` - 주문 조회
- `DELETE /orders/{order_id}` - 주문 취소
- `GET /orders` - 주문 목록 조회

### 오더북
- `GET /orderbook/{symbol}` - 오더북 조회
- `GET /orderbook/{symbol}/depth` - 오더북 깊이 조회

### 체결 내역
- `GET /trades` - 체결 내역 조회
- `GET /trades/{trade_id}` - 특정 체결 조회

### WebSocket
- `WS /ws/orderbook/{symbol}` - 실시간 오더북
- `WS /ws/trades/{symbol}` - 실시간 체결 내역

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해 주세요.
