from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.db.database import get_db
from app.services.trade_service import TradeService
from app.schemas.trade import TradeResponse, TradeListResponse

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """체결 조회"""
    trade_service = TradeService(db)
    trade = await trade_service.get_trade(trade_id)
    
    if not trade:
        raise HTTPException(status_code=404, detail="체결을 찾을 수 없습니다.")
    
    return TradeResponse.model_validate(trade)


@router.get("/", response_model=TradeListResponse)
async def get_trades(
    symbol: Optional[str] = Query(None, description="거래 심볼"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(100, ge=1, le=1000, description="조회 개수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    db: AsyncSession = Depends(get_db)
):
    """체결 목록 조회"""
    trade_service = TradeService(db)
    trades = await trade_service.get_trades(
        symbol=symbol,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        offset=offset
    )
    
    # 모델을 스키마로 변환
    trade_responses = [TradeResponse.model_validate(trade) for trade in trades]
    
    return TradeListResponse(
        trades=trade_responses,
        total=len(trades),  # 실제로는 전체 개수를 별도로 조회해야 함
        page=offset // limit + 1,
        size=limit
    )


@router.get("/symbol/{symbol}", response_model=TradeListResponse)
async def get_trades_by_symbol(
    symbol: str,
    limit: int = Query(100, ge=1, le=1000, description="조회 개수"),
    db: AsyncSession = Depends(get_db)
):
    """특정 심볼의 체결 내역 조회"""
    trade_service = TradeService(db)
    trades = await trade_service.get_trades_by_symbol(symbol, limit)
    
    # 모델을 스키마로 변환
    trade_responses = [TradeResponse.model_validate(trade) for trade in trades]
    
    return TradeListResponse(
        trades=trade_responses,
        total=len(trades),
        page=1,
        size=limit
    ) 