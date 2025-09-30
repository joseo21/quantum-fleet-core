from enum import Enum
from sqlalchemy import Column, Integer, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class RoleEnum(str, Enum):
    admin = "admin"
    manager = "manager"
    viewer = "viewer"


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_user_tenant_role"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(SAEnum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.viewer)

    user = relationship("User", backref="roles")
    tenant = relationship("Tenant", backref="user_roles")
