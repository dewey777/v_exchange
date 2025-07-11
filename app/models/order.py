from sqlalchemy import Column, String, Numeric, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum
import uuid

from app.db.database import Base


class OrderSide(str, enum.Enum):
    """주문 방향"""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, enum.Enum):
    """주문 타입"""
    LIMIT = "limit"
    MARKET = "market"
    IOC = "ioc"  # Immediate or Cancel


class OrderStatus(str, enum.Enum):
    """주문 상태"""
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Order(Base):
    """주문 테이블"""
    __tablename__ = "orders"

    # 기본 정보
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)  # 예: BTCUSDT
    side = Column(Enum(OrderSide), nullable=False)  # buy/sell
    order_type = Column(Enum(OrderType), nullable=False)  # limit/market/ioc
    
    # 가격 및 수량
    price = Column(Numeric(20, 8), nullable=True)  # Market 주문의 경우 NULL
    quantity = Column(Numeric(20, 8), nullable=False)
    filled_quantity = Column(Numeric(20, 8), nullable=False, default=0)
    remaining_quantity = Column(Numeric(20, 8), nullable=False, default=0)
    
    # 상태 및 시간
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.OPEN)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 추가 정보 (선택사항)
    user_id = Column(String(50), nullable=True, index=True)  # 추후 사용자 시스템 연동
    client_order_id = Column(String(100), nullable=True)  # 클라이언트가 지정한 주문 ID
    
    def __repr__(self):
        return f"<Order(id={self.id}, symbol={self.symbol}, side={self.side}, type={self.order_type}, price={self.price}, quantity={self.quantity}, status={self.status})>" 