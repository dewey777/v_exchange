from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, cast
from uuid import UUID
from datetime import datetime

from app.db.database import get_db
from app.services.order_service import OrderService
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    OrderCancelRequest,
    OrderCancelResponse
)
from app.models.order import OrderStatus

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """주문 생성"""
    try:
        order_service = OrderService(db)
        order = await order_service.create_order(order_data)
        return OrderResponse.model_validate(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="주문 생성 중 오류가 발생했습니다.")


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """주문 조회"""
    order_service = OrderService(db)
    order = await order_service.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    
    return OrderResponse.model_validate(order)


@router.get("/", response_model=OrderListResponse)
async def get_orders(
    symbol: Optional[str] = Query(None, description="거래 심볼"),
    user_id: Optional[str] = Query(None, description="사용자 ID"),
    status: Optional[OrderStatus] = Query(None, description="주문 상태"),
    limit: int = Query(100, ge=1, le=1000, description="조회 개수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    db: AsyncSession = Depends(get_db)
):
    """주문 목록 조회"""
    order_service = OrderService(db)
    orders = await order_service.get_orders(
        symbol=symbol,
        user_id=user_id,
        status=status,
        limit=limit,
        offset=offset
    )
    
    # 모델을 스키마로 변환
    order_responses = [OrderResponse.model_validate(order) for order in orders]
    
    return OrderListResponse(
        orders=order_responses,
        total=len(orders),  # 실제로는 전체 개수를 별도로 조회해야 함
        page=offset // limit + 1,
        size=limit
    )


@router.delete("/{order_id}", response_model=OrderCancelResponse)
async def cancel_order(
    order_id: UUID,
    cancel_request: OrderCancelRequest,
    db: AsyncSession = Depends(get_db)
):
    """주문 취소"""
    order_service = OrderService(db)
    
    try:
        order = await order_service.cancel_order(
            order_id=order_id,
            user_id=cancel_request.user_id
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
        
        return OrderCancelResponse(
            order_id=cast(UUID, order.id),
            status=cast(OrderStatus, order.status),
            cancelled_at=cast(datetime, order.updated_at),
            message="주문이 성공적으로 취소되었습니다."
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="주문 취소 중 오류가 발생했습니다.") 