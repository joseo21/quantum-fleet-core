import os
class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://quantum:quantum123@postgres:5432/quantumfleet")
    JWT_SECRET = os.getenv("JWT_SECRET", "dev")
    JWT_ALG = os.getenv("JWT_ALG", "HS256")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "43200"))
settings = Settings()
