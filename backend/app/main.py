from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import tenants, users, devices, ingest_http, telemetry
from .routers import admin_roles   # 👈 nuevo router de roles
from .routers import dashboards
from app.routers.ingest_teltonika import router as ingest_teltonika_router

app = FastAPI(title="Quantum Fleet Core", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En PROD, restringir al dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenants.router)
app.include_router(users.router)
app.include_router(devices.router)
app.include_router(ingest_http.router)
app.include_router(telemetry.router)
app.include_router(admin_roles.router)  # 👈 registro del router de roles
app.include_router(dashboards.router)
app.include_router(ingest_teltonika_router)

@app.get("/health")
def health():
    return {"status": "ok"}
