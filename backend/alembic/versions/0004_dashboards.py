"""Dashboards multi-tenant: dashboards + dashboard_panels (+ saved_queries base)

Revision ID: 0004_dashboards
Revises: 0003_fk_cascade
Create Date: 2025-09-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revisiones
revision = "0004_dashboards"
down_revision = "0003_fk_cascade"
branch_labels = None
depends_on = None


def upgrade():
    # jsonb
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")  # útil para UUID si se usa a futuro
    # (jsonb está por defecto disponible en Postgres 16)

    # Tabla dashboards (por tenant)
    op.create_table(
        "dashboards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "name", name="uq_dashboards_tenant_name"),
    )

    # Tabla panels (widgets) por dashboard
    op.create_table(
        "dashboard_panels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dashboard_id", sa.Integer(), sa.ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("type", sa.String(40), nullable=False),  # timeseries | stat | table | map (futuro)
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        # layout grid (x,y,w,h) – integers simples
        sa.Column("x", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("y", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("w", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("h", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
    )

    # (Opcional) saved_queries por tenant – base mínima para reuso futuro
    op.create_table(
        "saved_queries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("query", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "name", name="uq_saved_queries_tenant_name"),
    )


def downgrade():
    op.drop_table("saved_queries")
    op.drop_table("dashboard_panels")
    op.drop_table("dashboards")
