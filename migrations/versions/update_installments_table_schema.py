"""Update installments table schema

Revision ID: update_installments_schema
Revises: 4bfa945b175b
Create Date: 2025-12-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_installments_schema'
down_revision = '4bfa945b175b'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('installments', sa.Column('days', sa.Integer(), nullable=True))
    op.add_column('installments', sa.Column('percentage', sa.Numeric(precision=5, scale=2), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE installments SET days = 0 WHERE days IS NULL")
    op.execute("UPDATE installments SET percentage = 0 WHERE percentage IS NULL")
    
    # Make columns non-nullable
    op.alter_column('installments', 'days', nullable=False)
    op.alter_column('installments', 'percentage', nullable=False)
    
    # Remove old columns
    op.drop_column('installments', 'status')
    op.drop_column('installments', 'type')
    op.drop_column('installments', 'sequence_number')


def downgrade():
    # Add back old columns
    op.add_column('installments', sa.Column('sequence_number', sa.Integer(), nullable=True))
    op.add_column('installments', sa.Column('type', sa.String(), nullable=True))
    op.add_column('installments', sa.Column('status', sa.String(), nullable=True))
    
    # Set default values
    op.execute("UPDATE installments SET sequence_number = 1 WHERE sequence_number IS NULL")
    op.execute("UPDATE installments SET type = 'installment' WHERE type IS NULL")
    op.execute("UPDATE installments SET status = 'unpaid' WHERE status IS NULL")
    
    # Make columns non-nullable
    op.alter_column('installments', 'sequence_number', nullable=False)
    
    # Remove new columns
    op.drop_column('installments', 'percentage')
    op.drop_column('installments', 'days')

