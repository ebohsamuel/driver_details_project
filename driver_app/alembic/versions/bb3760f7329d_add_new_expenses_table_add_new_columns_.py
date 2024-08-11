"""Add new expenses table, add new columns to trips table, remove column from the drivers table

Revision ID: bb3760f7329d
Revises: 
Create Date: 2024-08-06 19:46:55.657310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb3760f7329d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new column 'age' to 'user' table
    op.add_column('trips', sa.Column('dispatch', sa.Integer))
    op.add_column('trips', sa.Column('bonus', sa.Integer))
    op.add_column('trips', sa.Column('diesel_litres', sa.Float))
    op.add_column('trips', sa.Column('diesel_amount', sa.Integer))
    op.add_column('trips', sa.Column('diesel_date', sa.Date))

    # Remove 'created_at' column from 'post' table
    op.drop_column('drivers', 'is_active')

    # Create 'comment' table
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('date', sa.Date, index=True),
        sa.Column('description', sa.String),
        sa.Column('driver_id', sa.Integer, sa.ForeignKey('drivers.id')),
        sa.Column('amount', sa.Integer)
    )


def downgrade() -> None:
    # Drop 'expenses' table
    op.drop_table('expenses')

    # Add back 'is_active' column to 'drivers' table
    op.add_column('drivers', sa.Column('is_active', sa.Boolean, default=True))

    # Remove columns from 'trips' table
    op.drop_column('trips', 'dispatch')
    op.drop_column('trips', 'bonus')
    op.drop_column('trips', 'diesel_litres')
    op.drop_column('trips', 'diesel_amount')
    op.drop_column('trips', 'diesel_date')