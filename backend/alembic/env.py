# backend/alembic/env.py
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- asegura que /app (raíz del backend en el contenedor) esté en PYTHONPATH
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Importa tu metadata para que Alembic vea TODAS las tablas
from app.database import Base  # noqa: F401
from app import models, models_dashboards, models_rbac  # noqa: F401

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

# Construye una URL confiable:
def _database_url() -> str:
    # 1) Si ya existe DATABASE_URL en el entorno, úsala
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # 2) Fallback con POSTGRES_* (coincide con tu .env / docker-compose)
    user = os.getenv("POSTGRES_USER", "quantum")
    password = os.getenv("POSTGRES_PASSWORD", "quantum123")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "quantumfleet")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"

DB_URL = _database_url()

# Fuerza la URL para que Alembic nunca reciba None
config.set_main_option("sqlalchemy.url", DB_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
