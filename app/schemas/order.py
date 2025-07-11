from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.order import OrderSide, OrderType, OrderStatus


class OrderBase(BaseModel):
    """주문 기본 스키마"""
    symbol: str = Field(..., min_length=1, max_length=20, description="거래 심볼 (예: BTCUSDT)")
    side: OrderSide = Field(..., description="주문 방향 (buy/sell)")
    order_type: OrderType = Field(..., description="주문 타입 (limit/market/ioc)")
    quantity: Decimal = Field(..., gt=0, decimal_places=8, description="주문 수량")
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=8, description="주문 가격 (Market 주문은 생략)")
    user_id: Optional[str] = Field(None, max_length=50, description="사용자 ID")
    client_order_id: Optional[str] = Field(None, max_length=100, description="클라이언트 주문 ID")

    @validator('price')
    def validate_price(cls, v, values):
        """Market 주문이 아닌 경우 가격은 필수"""
        if values.get('order_type') != OrderType.MARKET and v is None:
            raise ValueError('Limit/IOC 주문은 가격이 필수입니다.')
        return v

    @validator('quantity')
    def validate_quantity(cls, v):
        """수량은 0보다 커야 함"""
        if v <= 0:
            raise ValueError('수량은 0보다 커야 합니다.')
        return v


class OrderCreate(OrderBase):
    """주문 생성 요청 스키마"""
    pass


class OrderResponse(OrderBase):
    """주문 응답 스키마"""
    id: UUID
    filled_quantity: Decimal
    remaining_quantity: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    """주문 업데이트 스키마 (취소용)"""
    status: OrderStatus = Field(..., description="주문 상태")


class OrderListResponse(BaseModel):
    """주문 목록 응답 스키마"""
    orders: list[OrderResponse]
    total: int
    page: int
    size: int


class OrderCancelRequest(BaseModel):
    """주문 취소 요청 스키마"""
    order_id: UUID = Field(..., description="취소할 주문 ID")
    user_id: Optional[str] = Field(None, description="사용자 ID (선택사항)")


class OrderCancelResponse(BaseModel):
    """주문 취소 응답 스키마"""
    order_id: UUID
    status: OrderStatus
    cancelled_at: datetime
    message: str 