"""Change deal_id to auto increment integer

Revision ID: change_deal_id_auto_increment
Revises: update_installments_schema
Create Date: 2025-12-10 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'change_deal_id_auto_increment'
down_revision = 'update_installments_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Drop foreign key constraints temporarily
    op.drop_constraint('installments_deal_id_fkey', 'installments', type_='foreignkey')
    op.drop_constraint('payments_deal_id_fkey', 'payments', type_='foreignkey')
    
    # Step 2: Drop primary key constraint
    op.drop_constraint('deals_pkey', 'deals', type_='primary')
    
    # Step 3: Create new deal_id column as integer
    op.add_column('deals', sa.Column('deal_id_new', sa.Integer(), nullable=True))
    
    # Step 4: Populate new deal_id with sequential numbers based on created_at
    op.execute("""
        WITH numbered_deals AS (
            SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) as rn
            FROM deals
        )
        UPDATE deals
        SET deal_id_new = numbered_deals.rn
        FROM numbered_deals
        WHERE deals.id = numbered_deals.id
    """)
    
    # Step 5: Create sequence for auto-increment
    op.execute("CREATE SEQUENCE deals_deal_id_seq")
    op.execute("SELECT setval('deals_deal_id_seq', COALESCE((SELECT MAX(deal_id_new) FROM deals), 1))")
    
    # Step 6: Update installments table - add new column and populate
    op.add_column('installments', sa.Column('deal_id_new', sa.Integer(), nullable=True))
    op.execute("""
        UPDATE installments
        SET deal_id_new = deals.deal_id_new
        FROM deals
        WHERE installments.deal_id::text = deals.id::text
    """)
    
    # Step 7: Update payments table - add new column and populate
    op.add_column('payments', sa.Column('deal_id_new', sa.Integer(), nullable=True))
    op.execute("""
        UPDATE payments
        SET deal_id_new = deals.deal_id_new
        FROM deals
        WHERE payments.deal_id::text = deals.id::text
    """)
    
    # Step 8: Drop old columns
    op.drop_column('installments', 'deal_id')
    op.drop_column('payments', 'deal_id')
    op.drop_column('deals', 'id')
    op.drop_column('deals', 'deal_number')
    
    # Step 9: Rename new columns
    op.alter_column('deals', 'deal_id_new', new_column_name='deal_id')
    op.alter_column('installments', 'deal_id_new', new_column_name='deal_id')
    op.alter_column('payments', 'deal_id_new', new_column_name='deal_id')
    
    # Step 10: Make deal_id primary key and set up auto-increment
    op.execute("ALTER TABLE deals ALTER COLUMN deal_id SET NOT NULL")
    op.create_primary_key('deals_pkey', 'deals', ['deal_id'])
    op.execute("ALTER SEQUENCE deals_deal_id_seq OWNED BY deals.deal_id")
    op.execute("ALTER TABLE deals ALTER COLUMN deal_id SET DEFAULT nextval('deals_deal_id_seq')")
    
    # Step 11: Make foreign key columns NOT NULL
    op.alter_column('installments', 'deal_id', nullable=False)
    op.alter_column('payments', 'deal_id', nullable=False)
    
    # Step 12: Recreate foreign key constraints
    op.create_foreign_key('installments_deal_id_fkey', 'installments', 'deals', ['deal_id'], ['deal_id'], ondelete='CASCADE')
    op.create_foreign_key('payments_deal_id_fkey', 'payments', 'deals', ['deal_id'], ['deal_id'], ondelete='CASCADE')


def downgrade():
    # Add back UUID id column
    op.add_column('deals', sa.Column('id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('deals', sa.Column('deal_number', sa.String(), nullable=True))
    
    # Generate UUIDs and deal_numbers
    op.execute("""
        UPDATE deals
        SET id = gen_random_uuid(),
            deal_number = 'DEAL-' || UPPER(SUBSTRING(gen_random_uuid()::text FROM 1 FOR 8))
    """)
    
    # Make id primary key
    op.alter_column('deals', 'id', nullable=False)
    op.create_primary_key('deals_pkey', 'deals', ['id'])
    
    # Update foreign keys in installments and payments
    op.add_column('installments', sa.Column('deal_id_old', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('payments', sa.Column('deal_id_old', postgresql.UUID(as_uuid=True), nullable=True))
    
    op.execute("""
        UPDATE installments
        SET deal_id_old = deals.id
        FROM deals
        WHERE installments.deal_id = deals.deal_id
    """)
    
    op.execute("""
        UPDATE payments
        SET deal_id_old = deals.id
        FROM deals
        WHERE payments.deal_id = deals.deal_id
    """)
    
    # Drop new columns and rename old ones
    op.drop_column('installments', 'deal_id')
    op.drop_column('payments', 'deal_id')
    op.alter_column('installments', 'deal_id_old', new_column_name='deal_id')
    op.alter_column('payments', 'deal_id_old', new_column_name='deal_id')
    
    # Drop deal_id column from deals
    op.drop_column('deals', 'deal_id')
    op.execute("DROP SEQUENCE IF EXISTS deals_deal_id_seq")
    
    # Recreate foreign keys
    op.create_foreign_key('installments_deal_id_fkey', 'installments', 'deals', ['deal_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('payments_deal_id_fkey', 'payments', 'deals', ['deal_id'], ['id'], ondelete='CASCADE')

