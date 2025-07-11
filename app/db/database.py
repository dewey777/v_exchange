from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
import os

# 데이터베이스 URL 설정
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://vexchange:xxx@localhost:5432/v_exchange"
)

# 비동기 엔진 생성
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 개발 환경에서 SQL 쿼리 로그 출력
    pool_pre_ping=True,
    pool_recycle=300,
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base 클래스 (모든 모델이 상속받을 클래스)
Base = declarative_base()

# 메타데이터 설정
metadata = MetaData()

# 데이터베이스 세션 의존성
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 