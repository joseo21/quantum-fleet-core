from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models_rbac import UserRole, RoleEnum
from ..models import User, Tenant
from ..utils.rbac import require_role, get_tenant_id

router = APIRouter(prefix="/tenants/{tenant_id}/users", tags=["roles"])


@router.post("/{user_id}/roles/{role}")
def set_role(
    user_id: int,
    role: RoleEnum,
    db: Session = Depends(get_db),
    ctx=Depends(require_role(RoleEnum.admin)),
    tenant_id: int = Depends(get_tenant_id),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    ur = (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.tenant_id == tenant_id)
        .first()
    )
    if not ur:
        ur = UserRole(user_id=user_id, tenant_id=tenant_id, role=role)
        db.add(ur)
    else:
        ur.role = role
    db.commit()
    return {"ok": True, "user_id": user_id, "tenant_id": tenant_id, "role": role.value}


@router.get("/{user_id}/roles")
def list_roles_for_user(
    user_id: int,
    db: Session = Depends(get_db),
    ctx=Depends(require_role(RoleEnum.manager)),
    tenant_id: int = Depends(get_tenant_id),
):
    ur = (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.tenant_id == tenant_id)
        .first()
    )
    if not ur:
        return {"roles": []}
    return {"roles": [{"tenant_id": tenant_id, "role": ur.role.value}]}
