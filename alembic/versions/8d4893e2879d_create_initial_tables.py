"""Create initial tables

Revision ID: 8d4893e2879d
Revises: 
Create Date: 2025-07-11 13:25:52.642096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8d4893e2879d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types
    orderside_enum = postgresql.ENUM('buy', 'sell', name='orderside')
    ordertype_enum = postgresql.ENUM('limit', 'market', 'ioc', name='ordertype')
    orderstatus_enum = postgresql.ENUM('open', 'partially_filled', 'filled', 'cancelled', 'rejected', name='orderstatus')
    
    orderside_enum.create(op.get_bind())
    ordertype_enum.create(op.get_bind())
    orderstatus_enum.create(op.get_bind())
    
    # Create orders table
    op.create_table('orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('side', orderside_enum, nullable=False),
        sa.Column('order_type', ordertype_enum, nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('filled_quantity', sa.Numeric(precision=20, scale=8), nullable=False, server_default='0'),
        sa.Column('remaining_quantity', sa.Numeric(precision=20, scale=8), nullable=False, server_default='0'),
        sa.Column('status', orderstatus_enum, nullable=False, server_default='open'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=True),
        sa.Column('client_order_id', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for orders table
    op.create_index(op.f('ix_orders_symbol'), 'orders', ['symbol'], unique=False)
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)
    
    # Create trades table
    op.create_table('trades',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('buy_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sell_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('executed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['buy_order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['sell_order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for trades table
    op.create_index(op.f('ix_trades_symbol'), 'trades', ['symbol'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_trades_symbol'), table_name='trades')
    op.drop_table('trades')
    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_symbol'), table_name='orders')
    op.drop_table('orders')
    
    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS orderstatus')
    op.execute('DROP TYPE IF EXISTS ordertype')
    op.execute('DROP TYPE IF EXISTS orderside')
