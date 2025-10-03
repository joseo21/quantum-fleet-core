# backend/alembic/versions/20251003_add_telemetry_indexes.py
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251003_add_telemetry_indexes"
down_revision = None  # cámbialo por la última de tu repo si aplica
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_telemetry_tenant_device_ts
            ON telemetry (tenant_id, device_id, ts DESC);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_telemetry_ts
            ON telemetry (ts DESC);
    """)

def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_telemetry_tenant_device_ts;")
    op.execute("DROP INDEX IF EXISTS ix_telemetry_ts;")
