from alembic import op

# IDs de alembic
revision = "20251007_bootstrap_devices_telemetry"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 1) Si existe 'device' en singular y NO existe 'devices', renombrar
    op.execute("""
    DO $$
    BEGIN
        IF to_regclass('public.device') IS NOT NULL
           AND to_regclass('public.devices') IS NULL THEN
            ALTER TABLE public.device RENAME TO devices;
        END IF;
    END $$;
    """)

    # 2) Crear 'devices' si no existe
    op.execute("""
    CREATE TABLE IF NOT EXISTS public.devices (
        id SERIAL PRIMARY KEY,
        tenant_id INTEGER NULL,
        name VARCHAR(255) NOT NULL,
        external_id VARCHAR(64) UNIQUE,
        token VARCHAR(128) UNIQUE,
        settings JSONB DEFAULT '{}'::jsonb
    );
    """)

    # Asegurar columna settings (por si la tabla ya existía sin ella)
    op.execute("""
    ALTER TABLE public.devices
    ADD COLUMN IF NOT EXISTS settings JSONB DEFAULT '{}'::jsonb;
    """)

    # 3) Crear 'telemetry' si no existe
    op.execute("""
    CREATE TABLE IF NOT EXISTS public.telemetry (
        id BIGSERIAL PRIMARY KEY,
        device_id INTEGER NOT NULL REFERENCES public.devices(id) ON DELETE CASCADE,
        ts TIMESTAMPTZ NOT NULL DEFAULT now(),
        data JSONB NOT NULL
    );
    """)

    # 4) Índices útiles
    op.execute("CREATE INDEX IF NOT EXISTS ix_devices_external_id ON public.devices (external_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_devices_token ON public.devices (token);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telemetry_device_ts ON public.telemetry (device_id, ts DESC);")

def downgrade():
# convertido a comentario python
    pass
