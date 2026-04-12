from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.database import Base

if TYPE_CHECKING:
    from app.models.todo import Todo
    from app.models.work_log import WorkLog
    from app.models.report import Report
    from app.models.report_template import ReportTemplate


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    todos: Mapped[List["Todo"]] = relationship("Todo", back_populates="user", cascade="all, delete-orphan")
    work_logs: Mapped[List["WorkLog"]] = relationship("WorkLog", back_populates="user", cascade="all, delete-orphan")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    templates: Mapped[List["ReportTemplate"]] = relationship("ReportTemplate", back_populates="user", cascade="all, delete-orphan")
