"""create initial tables

Revision ID: ${revision_id}
Revises: None
Create Date: ${create_date}

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create trades table
    op.create_table('trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=True),
        sa.Column('side', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('filled_price', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create grid_bots table
    op.create_table('grid_bots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=True),
        sa.Column('lower_price', sa.Float(), nullable=True),
        sa.Column('upper_price', sa.Float(), nullable=True),
        sa.Column('grid_levels', sa.Integer(), nullable=True),
        sa.Column('amount_per_grid', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('stopped_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create dca_bots table
    op.create_table('dca_bots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=True),
        sa.Column('amount_per_period', sa.Float(), nullable=True),
        sa.Column('interval_days', sa.Integer(), nullable=True),
        sa.Column('total_periods', sa.Integer(), nullable=True),
        sa.Column('completed_periods', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('next_buy_date', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('trades')
    op.drop_table('grid_bots')
    op.drop_table('dca_bots')
    op.drop_table('audit_logs')