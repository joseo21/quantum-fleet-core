"""RBAC multi-tenant: user_roles + enum role_enum

Revision ID: 0002_rbac
Revises: 0001_init
Create Date: 2025-09-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_rbac"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade():
    # 1) Crear la ENUM solo si no existe (idempotente)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'role_enum' AND n.nspname = 'public'
            ) THEN
                CREATE TYPE role_enum AS ENUM ('admin', 'manager', 'viewer');
            END IF;
        END
        $$;
        """
    )

    # 2) Usar el tipo existente sin recrearlo
    role_enum_existing = postgresql.ENUM(
        name="role_enum",
        create_type=False,
    )

    op.create_table(
        "user_roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", role_enum_existing, nullable=False, server_default="viewer"),
    )
    op.create_unique_constraint("uq_user_tenant_role", "user_roles", ["user_id", "tenant_id"])


def downgrade():
    op.drop_constraint("uq_user_tenant_role", "user_roles", type_="unique")
    op.drop_table("user_roles")

    # 3) Eliminar el tipo solo si ya no lo usa ninguna columna
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                JOIN pg_type t ON a.atttypid = t.oid
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'role_enum'
                  AND n.nspname = 'public'
                  AND c.relkind IN ('r','p')
            ) THEN
                DROP TYPE IF EXISTS role_enum;
            END IF;
        END
        $$;
        """
    )
