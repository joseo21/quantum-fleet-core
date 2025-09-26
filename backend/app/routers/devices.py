from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from secrets import token_urlsafe
from ..database import get_db
from ..models import Device, Tenant
from ..schemas import DeviceCreate, DeviceOut
from ..auth import get_current_user

router = APIRouter(prefix="/devices", tags=["devices"])

@router.post("", response_model=DeviceOut)
def create_device(body: DeviceCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.tenant_id != body.tenant_id:
        raise HTTPException(403, "Cross-tenant not allowed")
    if not db.get(Tenant, body.tenant_id):
        raise HTTPException(400, "Tenant not found")
    d = Device(name=body.name, external_id=body.external_id, tenant_id=body.tenant_id, token=token_urlsafe(24))
    db.add(d); db.commit(); db.refresh(d); return d

@router.get("", response_model=list[DeviceOut])
def list_devices(db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(Device).filter(Device.tenant_id==user.tenant_id).order_by(Device.id)
    return q.all()
