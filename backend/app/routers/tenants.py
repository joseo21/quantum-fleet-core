from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Tenant
from ..schemas import TenantCreate, TenantOut

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.post("", response_model=TenantOut)
def create_tenant(body: TenantCreate, db: Session = Depends(get_db)):
    t = Tenant(name=body.name, slug=body.slug)
    db.add(t); db.commit(); db.refresh(t); return t

@router.get("", response_model=list[TenantOut])
def list_tenants(db: Session = Depends(get_db)):
    return db.query(Tenant).order_by(Tenant.id).all()
