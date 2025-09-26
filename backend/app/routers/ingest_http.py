from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Device, Telemetry
from ..schemas import TelemetryIn

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/http")
def ingest_http(body: TelemetryIn, db: Session = Depends(get_db)):
    dev = db.query(Device).filter(Device.token==body.token).first()
    if not dev: raise HTTPException(401, "Invalid token")
    tel = Telemetry(
        tenant_id=dev.tenant_id,
        device_id=dev.id,
        ts=body.ts or datetime.utcnow(),
        data=body.data
    )
    db.add(tel); db.commit()
    return {"ok": True, "device_id": dev.id}
