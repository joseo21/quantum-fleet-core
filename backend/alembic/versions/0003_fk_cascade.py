"""FK cascadas en telemetry (device_id y tenant_id)

Revision ID: 0003_fk_cascade
Revises: 0002_rbac
Create Date: 2025-09-30
"""
from alembic import op

# Revisiones
revision = "0003_fk_cascade"
down_revision = "0002_rbac"
branch_labels = None
depends_on = None


def upgrade():
    # Asegurar ON DELETE CASCADE en telemetry.device_id -> devices.id
    op.execute(
        """
        DO $$
        DECLARE
            fk_name text;
        BEGIN
            SELECT c.conname INTO fk_name
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
            JOIN pg_class rt ON rt.oid = c.confrelid
            JOIN pg_attribute ra ON ra.attrelid = rt.oid AND ra.attnum = ANY(c.confkey)
            WHERE t.relname = 'telemetry'
              AND c.contype = 'f'
              AND a.attname = 'device_id'
              AND rt.relname = 'devices'
              AND ra.attname = 'id';

            IF fk_name IS NOT NULL THEN
                EXECUTE format('ALTER TABLE telemetry DROP CONSTRAINT %I', fk_name);
            END IF;

            ALTER TABLE telemetry
              ADD CONSTRAINT telemetry_device_id_fkey
              FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE;
        END
        $$;
        """
    )

    # Asegurar ON DELETE CASCADE en telemetry.tenant_id -> tenants.id (opcional pero recomendado)
    op.execute(
        """
        DO $$
        DECLARE
            fk_name text;
        BEGIN
            SELECT c.conname INTO fk_name
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
            JOIN pg_class rt ON rt.oid = c.confrelid
            JOIN pg_attribute ra ON ra.attrelid = rt.oid AND ra.attnum = ANY(c.confkey)
            WHERE t.relname = 'telemetry'
              AND c.contype = 'f'
              AND a.attname = 'tenant_id'
              AND rt.relname = 'tenants'
              AND ra.attname = 'id';

            IF fk_name IS NOT NULL THEN
                EXECUTE format('ALTER TABLE telemetry DROP CONSTRAINT %I', fk_name);
            END IF;

            ALTER TABLE telemetry
              ADD CONSTRAINT telemetry_tenant_id_fkey
              FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE;
        END
        $$;
        """
    )


def downgrade():
    # Revertir a NO ACTION (sin cascada) en ambas FKs
    op.execute(
        """
        DO $$
        DECLARE
            fk_name text;
        BEGIN
            -- device_id
            SELECT c.conname INTO fk_name
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
            JOIN pg_class rt ON rt.oid = c.confrelid
            JOIN pg_attribute ra ON ra.attrelid = rt.oid AND ra.attnum = ANY(c.confkey)
            WHERE t.relname = 'telemetry'
              AND c.contype = 'f'
              AND a.attname = 'device_id'
              AND rt.relname = 'devices'
              AND ra.attname = 'id';

            IF fk_name IS NOT NULL THEN
                EXECUTE format('ALTER TABLE telemetry DROP CONSTRAINT %I', fk_name);
            END IF;

            ALTER TABLE telemetry
              ADD CONSTRAINT telemetry_device_id_fkey
              FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE NO ACTION;

            -- tenant_id
            SELECT c.conname INTO fk_name
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
            JOIN pg_class rt ON rt.oid = c.confrelid
            JOIN pg_attribute ra ON ra.attrelid = rt.oid AND ra.attnum = ANY(c.confkey)
            WHERE t.relname = 'telemetry'
              AND c.contype = 'f'
              AND a.attname = 'tenant_id'
              AND rt.relname = 'tenants'
              AND ra.attname = 'id';

            IF fk_name IS NOT NULL THEN
                EXECUTE format('ALTER TABLE telemetry DROP CONSTRAINT %I', fk_name);
            END IF;

            ALTER TABLE telemetry
              ADD CONSTRAINT telemetry_tenant_id_fkey
              FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE NO ACTION;
        END
        $$;
        """
    )
