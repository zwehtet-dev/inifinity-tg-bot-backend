"""Add webhook configuration models

Revision ID: add_webhook_models
Revises: 2554dafbb68a
Create Date: 2025-01-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_webhook_models'
down_revision = '2554dafbb68a'
branch_labels = None
depends_on = None


def upgrade():
    # Create webhook_logs table
    op.create_table(
        'webhook_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create bot_webhook_settings table
    op.create_table(
        'bot_webhook_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('webhook_url', sa.String(length=255), nullable=False),
        sa.Column('secret', sa.String(length=255), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('bot_webhook_settings')
    op.drop_table('webhook_logs')
