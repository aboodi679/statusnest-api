"""add service_status table

Revision ID: 750b1f0768b3
Revises: 3e3dcba1e407
Create Date: 2026-07-01 19:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '750b1f0768b3'
down_revision: Union[str, None] = '3e3dcba1e407'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'service_status',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('service_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('checked_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_service_status_service_id', 'service_status', ['service_id'])
    op.create_index('ix_service_status_checked_at', 'service_status', ['checked_at'])


def downgrade() -> None:
    op.drop_index('ix_service_status_checked_at', table_name='service_status')
    op.drop_index('ix_service_status_service_id', table_name='service_status')
    op.drop_table('service_status')