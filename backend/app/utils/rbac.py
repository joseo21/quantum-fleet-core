from fastapi import Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user
from ..models_rbac import UserRole, RoleEnum
from ..models import Tenant

# Orden de privilegios: viewer < manager < admin
ROLE_ORDER = {RoleEnum.viewer: 0, RoleEnum.manager: 1, RoleEnum.admin: 2}


def get_tenant_id(
    request: Request,
    x_tenant_id: int | None = Header(default=None, convert_underscores=False),
    user=Depends(get_current_user),
) -> int:
    """
    Obtiene tenant_id en este orden:
    1) De la ruta si existe {tenant_id}
    2) Del header X-Tenant-ID
    3) Del tenant_id del usuario autenticado (fallback compatible)
    """
    # 1) Path param
    if "tenant_id" in request.path_params:
        return int(request.path_params["tenant_id"])

    # 2) Header
    if x_tenant_id is not None:
        return int(x_tenant_id)

    # 3) Fallback al tenant del usuario
    if getattr(user, "tenant_id", None) is not None:
        return int(user.tenant_id)

    raise HTTPException(status_code=400, detail="tenant_id requerido (path, X-Tenant-ID o usuario)")


def require_role(min_role: RoleEnum):
    """
    Dependencia de ruta para exigir un rol mínimo dentro del tenant resuelto.
    Retorna dict con { tenant_id, role } por si quieres usarlo en el handler.
    """
    def _dep(
        db: Session = Depends(get_db),
        user=Depends(get_current_user),
        tenant_id: int = Depends(get_tenant_id),
    ):
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant no encontrado")

        ur = (
            db.query(UserRole)
            .filter(UserRole.user_id == user.id, UserRole.tenant_id == tenant_id)
            .first()
        )
        if not ur:
            raise HTTPException(status_code=403, detail="Sin rol asignado en este tenant")

        if ROLE_ORDER[ur.role] < ROLE_ORDER[min_role]:
            raise HTTPException(status_code=403, detail=f"Se requiere rol {min_role.value}")

        return {"tenant_id": tenant_id, "role": ur.role}

    return _dep
