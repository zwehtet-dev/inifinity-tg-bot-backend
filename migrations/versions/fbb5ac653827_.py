"""empty message

Revision ID: fbb5ac653827
Revises: 9ec1623b0b6c
Create Date: 2025-07-20 10:31:52.143852

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbb5ac653827'
down_revision = '9ec1623b0b6c'
branch_labels = None
depends_on = None


def upgrade():
    try:
        with op.batch_alter_table('orders', schema=None) as batch_op:
            batch_op.add_column(sa.Column('telegram_id', sa.String(length=255), nullable=False))
            batch_op.create_foreign_key('fk_orders_telegram_id', 'telegram_ids', ['telegram_id'], ['telegram_id'])
    except Exception as e:
        print(f"Upgrade failed: {e}")

def downgrade():
    try:
        with op.batch_alter_table('orders', schema=None) as batch_op:
            batch_op.drop_constraint('fk_orders_telegram_id', type_='foreignkey')
            batch_op.drop_column('telegram_id')
    except Exception as e:
        print(f"Downgrade failed: {e}")
