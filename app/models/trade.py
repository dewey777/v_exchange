from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Trade(Base):
    """체결 테이블"""
    __tablename__ = "trades"

    # 기본 정보
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 주문 참조
    buy_order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    sell_order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    
    # 체결 정보
    symbol = Column(String(20), nullable=False, index=True)  # 예: BTCUSDT
    price = Column(Numeric(20, 8), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    
    # 시간 정보
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 관계 설정
    buy_order = relationship("Order", foreign_keys=[buy_order_id])
    sell_order = relationship("Order", foreign_keys=[sell_order_id])
    
    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, price={self.price}, quantity={self.quantity}, executed_at={self.executed_at})>" 