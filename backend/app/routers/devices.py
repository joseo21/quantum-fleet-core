from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from secrets import token_urlsafe

from ..utils.rbac import require_role
from ..models_rbac import RoleEnum

from ..database import get_db
from ..models import Device, Tenant
from ..schemas import DeviceCreate, DeviceOut
from ..auth import get_current_user


router = APIRouter(prefix="/devices", tags=["devices"])


# ---------- MODELOS LOCALES (para PATCH) ----------
class DevicePatch(BaseModel):
    name: Optional[str] = None
    external_id: Optional[str] = None
    # No permitimos cambiar tenant por PATCH aquí para evitar cross-tenant.


# ---------- CREATE ----------
@router.post(
    "",
    response_model=DeviceOut,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def create_device(
    body: DeviceCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Seguridad de tenant
    if user.tenant_id != body.tenant_id:
        raise HTTPException(403, "Cross-tenant not allowed")
    if not db.get(Tenant, body.tenant_id):
        raise HTTPException(400, "Tenant not found")

    d = Device(
        name=body.name,
        external_id=body.external_id,
        tenant_id=body.tenant_id,
        token=token_urlsafe(24),
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


# ---------- LIST ----------
@router.get(
    "",
    response_model=list[DeviceOut],
    dependencies=[Depends(require_role(RoleEnum.viewer))],
)
def list_devices(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Device).filter(Device.tenant_id == user.tenant_id).order_by(Device.id)
    return q.all()


# ---------- PUT (reemplazo completo) ----------
@router.put(
    "/{device_id}",
    response_model=DeviceOut,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def put_device(
    device_id: int,
    body: DeviceCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    dev = db.get(Device, device_id)
    if not dev:
        raise HTTPException(404, "Device not found")

    # El device debe pertenecer al mismo tenant del usuario
    if dev.tenant_id != user.tenant_id:
        raise HTTPException(403, "Cross-tenant not allowed (resource)")

    # Y el payload no debe intentar cambiar de tenant
    if body.tenant_id != user.tenant_id:
        raise HTTPException(403, "Cross-tenant not allowed (payload)")

    # Validamos existencia de tenant
    if not db.get(Tenant, body.tenant_id):
        raise HTTPException(400, "Tenant not found")

    dev.name = body.name
    dev.external_id = body.external_id
    # dev.tenant_id = body.tenant_id  # (mantenemos igual por seguridad)
    db.commit()
    db.refresh(dev)
    return dev


# ---------- PATCH (parcial) ----------
@router.patch(
    "/{device_id}",
    response_model=DeviceOut,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def patch_device(
    device_id: int,
    body: DevicePatch,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    dev = db.get(Device, device_id)
    if not dev:
        raise HTTPException(404, "Device not found")

    if dev.tenant_id != user.tenant_id:
        raise HTTPException(403, "Cross-tenant not allowed (resource)")

    if body.name is not None:
        dev.name = body.name
    if body.external_id is not None:
        dev.external_id = body.external_id

    db.commit()
    db.refresh(dev)
    return dev


# ---------- DELETE ----------
@router.delete(
    "/{device_id}",
    status_code=204,
    dependencies=[Depends(require_role(RoleEnum.admin))],
)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    dev = db.get(Device, device_id)
    if not dev:
        raise HTTPException(404, "Device not found")

    if dev.tenant_id != user.tenant_id:
        raise HTTPException(403, "Cross-tenant not allowed (resource)")

    # Con ON DELETE CASCADE en DB, basta con borrar el device
    db.delete(dev)
    db.commit()
    return None
