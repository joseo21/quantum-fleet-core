from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None

def upgrade():
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("slug", sa.String(80), nullable=False, unique=True),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), index=True),
        sa.Column("email", sa.String(160), unique=True, index=True),
        sa.Column("password_hash", sa.String(256)),
        sa.Column("role", sa.String(20)),
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), index=True),
        sa.Column("name", sa.String(120)),
        sa.Column("external_id", sa.String(120), unique=True, index=True),
        sa.Column("token", sa.String(120), unique=True, index=True),
    )
    op.create_table(
        "telemetry",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), index=True),
        sa.Column("device_id", sa.Integer, sa.ForeignKey("devices.id"), index=True),
        sa.Column("ts", sa.DateTime, index=True),
        sa.Column("data", sa.JSON),
    )
    op.create_index("ix_telemetry_tenant_device_ts", "telemetry", ["tenant_id","device_id","ts"], unique=False)

def downgrade():
    op.drop_index("ix_telemetry_tenant_device_ts", table_name="telemetry")
    op.drop_table("telemetry")
    op.drop_table("devices")
    op.drop_table("users")
    op.drop_table("tenants")
