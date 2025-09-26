from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User

# Punto de emisión del token tipo password (se usa en /auth/login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_token(sub: str, role: str, tenant_id: int) -> str:
    """
    Genera un JWT firmado para el usuario.
    sub: normalmente el email del usuario.
    """
    payload = {
        "sub": sub,
        "role": role,
        "tenant_id": tenant_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Decodifica el JWT, busca el usuario y lo retorna.
    Lanza 401 si el token no es válido o el usuario no existe.
    """
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        email = data.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token (no sub)")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
