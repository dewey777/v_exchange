from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


class OrderBookLevel(BaseModel):
    """오더북 레벨 스키마"""
    price: Decimal
    quantity: Decimal
    order_count: int


class OrderBookResponse(BaseModel):
    """오더북 응답 스키마"""
    symbol: str
    timestamp: datetime
    bids: List[OrderBookLevel]  # 매수 주문 (가격 내림차순)
    asks: List[OrderBookLevel]  # 매도 주문 (가격 오름차순)
    
    class Config:
        from_attributes = True


class OrderBookDepthResponse(BaseModel):
    """오더북 깊이 응답 스키마"""
    symbol: str
    timestamp: datetime
    depth: int
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]


class OrderBookFilter(BaseModel):
    """오더북 필터 스키마"""
    depth: Optional[int] = Field(20, ge=1, le=100, description="오더북 깊이") 