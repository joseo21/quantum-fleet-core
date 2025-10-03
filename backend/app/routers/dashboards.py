from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_user
from ..utils.rbac import require_role, get_tenant_id
from ..models_rbac import RoleEnum
from ..models_dashboards import Dashboard, DashboardPanel
from ..schemas_dashboards import (
    DashboardCreate, DashboardUpdate, DashboardOut,
    PanelCreate, PanelUpdate, PanelOut, DashboardWithPanels,
)

router = APIRouter(prefix="/tenants/{tenant_id}/dashboards", tags=["dashboards"])


# ---------- Helpers ----------
def _get_dashboard(db: Session, tenant_id: int, dashboard_id: int) -> Dashboard:
    d = db.query(Dashboard).filter(
        Dashboard.id == dashboard_id,
        Dashboard.tenant_id == tenant_id
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return d


def _get_panel(db: Session, tenant_id: int, dashboard_id: int, panel_id: int) -> DashboardPanel:
    p = db.query(DashboardPanel).join(Dashboard).filter(
        DashboardPanel.id == panel_id,
        DashboardPanel.dashboard_id == dashboard_id,
        Dashboard.tenant_id == tenant_id
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Panel not found")
    return p


# ---------- Dashboards ----------
@router.get(
    "",
    response_model=List[DashboardOut],
    dependencies=[Depends(require_role(RoleEnum.viewer))],
)
def list_dashboards(
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return (
        db.query(Dashboard)
        .filter(Dashboard.tenant_id == tenant_id)
        .order_by(Dashboard.id)
        .all()
    )


@router.post(
    "",
    response_model=DashboardOut,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def create_dashboard(
    body: DashboardCreate,
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    d = Dashboard(
        tenant_id=tenant_id,
        name=body.name,
        description=body.description,
        is_public=body.is_public,
        created_by=user.id,
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@router.get(
    "/{dashboard_id}",
    response_model=DashboardWithPanels,
    dependencies=[Depends(require_role(RoleEnum.viewer))],
)
def get_dashboard(
    dashboard_id: int = Path(..., ge=1),
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    d = _get_dashboard(db, tenant_id, dashboard_id)
    return DashboardWithPanels(
        id=d.id,
        tenant_id=d.tenant_id,
        name=d.name,
        description=d.description,
        is_public=d.is_public,
        created_by=d.created_by,
        created_at=d.created_at,
        updated_at=d.updated_at,
        panels=[PanelOut.model_validate(p) for p in d.panels],
    )


@router.put(
    "/{dashboard_id}",
    response_model=DashboardOut,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def update_dashboard_put(
    body: DashboardCreate,
    dashboard_id: int = Path(..., ge=1),
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    d = _get_dashboard(db, tenant_id, dashboard_id)
    d.name = body.name
    d.description = body.description
    d.is_public = body.is_public
    db.commit()
    db.refresh(d)
    return d


@router.patch(
    "/{dashboard_id}",
    response_model=DashboardOut,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def update_dashboard_patch(
    body: DashboardUpdate,
    dashboard_id: int = Path(..., ge=1),
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    d = _get_dashboard(db, tenant_id, dashboard_id)
    if body.name is not None:
        d.name = body.name
    if body.description is not None:
        d.description = body.description
    if body.is_public is not None:
        d.is_public = body.is_public
    db.commit()
    db.refresh(d)
    return d


@router.delete(
    "/{dashboard_id}",
    status_code=204,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def delete_dashboard(
    dashboard_id: int = Path(..., ge=1),
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    d = _get_dashboard(db, tenant_id, dashboard_id)
    db.delete(d)
    db.commit()
    return {"ok": True}


# ---------- Panels ----------
@router.post(
    "/{dashboard_id}/panels",
    response_model=PanelOut,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def create_panel(
    body: PanelCreate,
    dashboard_id: int = Path(..., ge=1),
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    d = _get_dashboard(db, tenant_id, dashboard_id)
    p = DashboardPanel(
        dashboard_id=d.id,
        title=body.title,
        type=body.type,
        config=body.config or {},
        x=body.x, y=body.y, w=body.w, h=body.h,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get(
    "/{dashboard_id}/panels/{panel_id}",
    response_model=PanelOut,
    dependencies=[Depends(require_role(RoleEnum.viewer))],
)
def get_panel(
    panel_id: int = Path(..., ge=1),
    dashboard_id: int = Path(..., ge=1),
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    p = _get_panel(db, tenant_id, dashboard_id, panel_id)
    return p


@router.put(
    "/{dashboard_id}/panels/{panel_id}",
    response_model=PanelOut,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def update_panel_put(
    body: PanelCreate,
    panel_id: int = Path(..., ge=1),
    dashboard_id: int = Path(..., ge=1),
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    p = _get_panel(db, tenant_id, dashboard_id, panel_id)
    p.title = body.title
    p.type = body.type
    p.config = body.config or {}
    p.x, p.y, p.w, p.h = body.x, body.y, body.w, body.h
    db.commit()
    db.refresh(p)
    return p


@router.patch(
    "/{dashboard_id}/panels/{panel_id}",
    response_model=PanelOut,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def update_panel_patch(
    body: PanelUpdate,
    panel_id: int = Path(..., ge=1),
    dashboard_id: int = Path(..., ge=1),
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    p = _get_panel(db, tenant_id, dashboard_id, panel_id)
    if body.title is not None:
        p.title = body.title
    if body.type is not None:
        p.type = body.type
    if body.config is not None:
        p.config = body.config
    if body.x is not None:
        p.x = body.x
    if body.y is not None:
        p.y = body.y
    if body.w is not None:
        p.w = body.w
    if body.h is not None:
        p.h = body.h
    db.commit()
    db.refresh(p)
    return p


@router.delete(
    "/{dashboard_id}/panels/{panel_id}",
    status_code=204,
    dependencies=[Depends(require_role(RoleEnum.manager))],
)
def delete_panel(
    panel_id: int = Path(..., ge=1),
    dashboard_id: int = Path(..., ge=1),
    tenant_id: int = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    p = _get_panel(db, tenant_id, dashboard_id, panel_id)
    db.delete(p)
    db.commit()
    return {"ok": True}
