from fastapi import Depends, HTTPException
from .auth import get_current_user
def require_admin(user=Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(403, "Admin only")
    return user
