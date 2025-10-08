"""merge heads

Revision ID: 137e7ce1a062
Revises: e01d72669daa, 20251007_bootstrap_devices_telemetry
Create Date: 2025-10-07 19:49:20.942900

"""
from alembic import op
import sqlalchemy as sa

revision = '137e7ce1a062'
down_revision = ('e01d72669daa', '20251007_bootstrap_devices_telemetry')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
