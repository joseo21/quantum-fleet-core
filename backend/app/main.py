from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import tenants, users, devices, ingest_http, telemetry
from .routers import admin_roles   # 👈 nuevo router de roles
from .routers import dashboards
from app.routers.ingest_teltonika import router as ingest_teltonika_router
from app.routers import telemetry_read
from app.routers import connectors
from app.routers import audit

app = FastAPI(title="API JOSE", version="0.1.0")

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
app.include_router(telemetry_read.router)
app.include_router(connectors.router)
app.include_router(audit.router, tags=["audit"])

@app.get("/health")
def health():
    return {"status": "ok"}
