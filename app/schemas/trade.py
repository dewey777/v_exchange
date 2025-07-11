from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import Optional


class TradeResponse(BaseModel):
    """체결 응답 스키마"""
    id: UUID
    buy_order_id: UUID
    sell_order_id: UUID
    symbol: str
    price: Decimal
    quantity: Decimal
    executed_at: datetime

    class Config:
        from_attributes = True


class TradeListResponse(BaseModel):
    """체결 목록 응답 스키마"""
    trades: list[TradeResponse]
    total: int
    page: int
    size: int


class TradeFilter(BaseModel):
    """체결 필터 스키마"""
    symbol: Optional[str] = Field(None, description="거래 심볼")
    start_time: Optional[datetime] = Field(None, description="시작 시간")
    end_time: Optional[datetime] = Field(None, description="종료 시간")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="조회 개수")
    offset: Optional[int] = Field(0, ge=0, description="오프셋") 