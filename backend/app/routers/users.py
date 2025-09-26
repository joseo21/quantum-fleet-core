from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Tenant
from ..schemas import UserCreate, UserOut
from ..utils.security import hash_password, verify_password
from ..auth import create_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if not db.get(Tenant, body.tenant_id):
        raise HTTPException(400, "Tenant not found")
    if db.query(User).filter(User.email==body.email).first():
        raise HTTPException(409, "Email already used")
    u = User(email=body.email, password_hash=hash_password(body.password),
             role=body.role, tenant_id=body.tenant_id)
    db.add(u); db.commit(); db.refresh(u); return u

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email==form.username).first()
    if not u or not verify_password(form.password, u.password_hash):
        raise HTTPException(401, "Bad credentials")
    token = create_token(u.email, u.role, u.tenant_id)
    return {"access_token": token, "token_type":"bearer", "role": u.role, "tenant_id": u.tenant_id}
