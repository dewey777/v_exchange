from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Sequence, cast
from decimal import Decimal
from uuid import UUID
import uuid
from datetime import datetime

from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate


class OrderService:
    """주문 서비스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_order(self, order_data: OrderCreate) -> Order:
        """주문 생성"""
        # 주문 데이터 준비
        order_dict = order_data.dict()
        order_dict['id'] = uuid.uuid4()
        order_dict['remaining_quantity'] = order_dict['quantity']
        order_dict['filled_quantity'] = Decimal('0')
        order_dict['status'] = OrderStatus.OPEN
        
        # Order 모델 인스턴스 생성
        order = Order(**order_dict)
        
        # 데이터베이스에 저장
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def get_order(self, order_id: UUID) -> Optional[Order]:
        """주문 조회"""
        query = select(Order).where(Order.id == order_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_orders(
        self, 
        symbol: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[OrderStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Sequence[Order]:
        """주문 목록 조회"""
        query = select(Order)
        
        # 필터 조건 추가
        conditions = []
        if symbol:
            conditions.append(Order.symbol == symbol)
        if user_id:
            conditions.append(Order.user_id == user_id)
        if status:
            conditions.append(Order.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 정렬 및 페이징
        query = query.order_by(Order.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def cancel_order(self, order_id: UUID, user_id: Optional[str] = None) -> Optional[Order]:
        """주문 취소"""
        # 주문 조회
        query = select(Order).where(Order.id == order_id)
        if user_id:
            query = query.where(Order.user_id == user_id)
        
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            return None
        
        # 취소 가능한 상태인지 확인
        if order.status not in [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]:
            raise ValueError(f"주문 상태가 취소 가능하지 않습니다: {order.status}")
        
        # 주문 상태를 취소로 변경 (타입 캐스팅 사용)
        setattr(order, 'status', OrderStatus.CANCELLED)
        setattr(order, 'updated_at', datetime.utcnow())
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def update_order_status(self, order_id: UUID, status: OrderStatus) -> Optional[Order]:
        """주문 상태 업데이트"""
        query = select(Order).where(Order.id == order_id)
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            return None
        
        # 타입 캐스팅 사용
        setattr(order, 'status', status)
        setattr(order, 'updated_at', datetime.utcnow())
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def update_order_filled_quantity(
        self, 
        order_id: UUID, 
        filled_quantity: Decimal
    ) -> Optional[Order]:
        """주문 체결 수량 업데이트"""
        query = select(Order).where(Order.id == order_id)
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            return None
        
        # 체결 수량 업데이트 (타입 캐스팅 사용)
        setattr(order, 'filled_quantity', filled_quantity)
        qty_val = Decimal(order.quantity)  # type: ignore
        setattr(order, 'remaining_quantity', qty_val - filled_quantity)
        
        # 상태 업데이트 (실제 값으로 비교)
        remaining_qty = qty_val - filled_quantity
        if remaining_qty == Decimal('0'):
            setattr(order, 'status', OrderStatus.FILLED)
        elif filled_quantity > Decimal('0'):
            setattr(order, 'status', OrderStatus.PARTIALLY_FILLED)
        
        setattr(order, 'updated_at', datetime.utcnow())
        
        await self.db.commit()
        await self.db.refresh(order)
        
        return order
    
    async def get_open_orders_by_symbol(self, symbol: str) -> Sequence[Order]:
        """특정 심볼의 미체결 주문 조회"""
        query = select(Order).where(
            and_(
                Order.symbol == symbol,
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED])
            )
        ).order_by(Order.created_at.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all() 