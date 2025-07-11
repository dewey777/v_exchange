from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Sequence
from decimal import Decimal
from uuid import UUID
import uuid
from datetime import datetime

from app.models.trade import Trade
from app.models.order import Order


class TradeService:
    """체결 서비스"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_trade(
        self,
        buy_order_id: UUID,
        sell_order_id: UUID,
        symbol: str,
        price: Decimal,
        quantity: Decimal
    ) -> Trade:
        """체결 생성"""
        trade = Trade(
            id=uuid.uuid4(),
            buy_order_id=buy_order_id,
            sell_order_id=sell_order_id,
            symbol=symbol,
            price=price,
            quantity=quantity,
            executed_at=datetime.utcnow()
        )
        
        self.db.add(trade)
        await self.db.commit()
        await self.db.refresh(trade)
        
        return trade
    
    async def get_trade(self, trade_id: UUID) -> Optional[Trade]:
        """체결 조회"""
        query = select(Trade).where(Trade.id == trade_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_trades(
        self,
        symbol: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Sequence[Trade]:
        """체결 목록 조회"""
        query = select(Trade)
        
        # 필터 조건 추가
        conditions = []
        if symbol:
            conditions.append(Trade.symbol == symbol)
        if start_time:
            conditions.append(Trade.executed_at >= start_time)
        if end_time:
            conditions.append(Trade.executed_at <= end_time)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 정렬 및 페이징
        query = query.order_by(Trade.executed_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_trades_by_order(self, order_id: UUID) -> Sequence[Trade]:
        """특정 주문의 체결 내역 조회"""
        query = select(Trade).where(
            (Trade.buy_order_id == order_id) | (Trade.sell_order_id == order_id)
        ).order_by(Trade.executed_at.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_trades_by_symbol(self, symbol: str, limit: int = 100) -> Sequence[Trade]:
        """특정 심볼의 최근 체결 내역 조회"""
        query = select(Trade).where(Trade.symbol == symbol)
        query = query.order_by(Trade.executed_at.desc())
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all() 