from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(160), nullable=False)
    description = Column(String(500))
    is_public = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # timestamps con defaults en DB y ORM
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        default=func.now(),
        onupdate=func.now(),
    )

    panels = relationship(
        "DashboardPanel",
        back_populates="dashboard",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DashboardPanel(Base):
    __tablename__ = "dashboard_panels"

    id = Column(Integer, primary_key=True)
    dashboard_id = Column(
        Integer,
        ForeignKey("dashboards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(160), nullable=False)
    type = Column(String(40), nullable=False)  # "timeseries", "stat", "table" ...

    config = Column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    # layout defaults
    x = Column(Integer, nullable=False, server_default=text("0"))
    y = Column(Integer, nullable=False, server_default=text("0"))
    w = Column(Integer, nullable=False, server_default=text("6"))
    h = Column(Integer, nullable=False, server_default=text("4"))

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    )

    dashboard = relationship("Dashboard", back_populates="panels")


class SavedQuery(Base):
    __tablename__ = "saved_queries"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(160), nullable=False)
    query = Column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        default=func.now(),
    )
