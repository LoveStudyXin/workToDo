from __future__ import annotations
from datetime import datetime, date
from sqlalchemy import String, Integer, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.todo import Todo


class WorkLog(Base):
    __tablename__ = "work_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    todo_id: Mapped[Optional[int]] = mapped_column(ForeignKey("todos.id"), nullable=True, index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    content: Mapped[str] = mapped_column(Text)
    hours_spent: Mapped[float] = mapped_column(Float, default=0)
    progress_update: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-100
    previous_progress: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 记录更新前的进度，用于删除时回退
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="work_logs")
    todo: Mapped[Optional["Todo"]] = relationship("Todo", back_populates="work_logs")
