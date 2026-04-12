from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.work_log import WorkLog
from app.models.todo import Todo

router = APIRouter(prefix="/api/work-logs", tags=["work-logs"])


class WorkLogCreate(BaseModel):
    date: date
    todo_id: Optional[int] = None
    content: str
    hours_spent: float = 0
    progress_update: Optional[int] = None
    notes: Optional[str] = None


class WorkLogUpdate(BaseModel):
    date: Optional[date] = None
    todo_id: Optional[int] = None
    content: Optional[str] = None
    hours_spent: Optional[float] = None
    progress_update: Optional[int] = None
    notes: Optional[str] = None


class TodoBrief(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class WorkLogResponse(BaseModel):
    id: int
    date: date
    todo_id: Optional[int]
    content: str
    hours_spent: float
    progress_update: Optional[int]
    notes: Optional[str]
    created_at: datetime
    todo: Optional[TodoBrief] = None

    class Config:
        from_attributes = True


@router.post("", response_model=WorkLogResponse)
async def create_work_log(
    log_data: WorkLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify todo belongs to user if provided
    previous_progress = None
    if log_data.todo_id:
        result = await db.execute(
            select(Todo).where(and_(Todo.id == log_data.todo_id, Todo.user_id == current_user.id))
        )
        todo = result.scalar_one_or_none()
        if not todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

        # Update todo progress if progress_update is provided
        if log_data.progress_update is not None:
            # 记录更新前的进度，用于删除时回退
            previous_progress = todo.progress

            todo.progress = log_data.progress_update
            # 根据进度自动设置状态
            if log_data.progress_update == 0:
                todo.status = "pending"
                todo.completed_at = None
            elif log_data.progress_update == 100:
                todo.status = "completed"
                if todo.completed_at is None:
                    todo.completed_at = datetime.utcnow()
            else:
                todo.status = "in_progress"
                todo.completed_at = None
            if log_data.hours_spent:
                todo.actual_hours = (todo.actual_hours or 0) + log_data.hours_spent

    work_log = WorkLog(
        user_id=current_user.id,
        date=log_data.date,
        todo_id=log_data.todo_id,
        content=log_data.content,
        hours_spent=log_data.hours_spent,
        progress_update=log_data.progress_update,
        previous_progress=previous_progress,
        notes=log_data.notes
    )
    db.add(work_log)
    await db.commit()

    # 重新查询以加载关联的 todo
    result = await db.execute(
        select(WorkLog).options(selectinload(WorkLog.todo)).where(WorkLog.id == work_log.id)
    )
    return result.scalar_one()


@router.get("", response_model=List[WorkLogResponse])
async def get_work_logs(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    todo_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(WorkLog).options(selectinload(WorkLog.todo)).where(WorkLog.user_id == current_user.id)

    if start_date:
        query = query.where(WorkLog.date >= start_date)
    if end_date:
        query = query.where(WorkLog.date <= end_date)
    if todo_id:
        query = query.where(WorkLog.todo_id == todo_id)

    query = query.order_by(WorkLog.date.desc(), WorkLog.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/today", response_model=List[WorkLogResponse])
async def get_today_work_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    today = date.today()
    query = select(WorkLog).options(selectinload(WorkLog.todo)).where(
        and_(WorkLog.user_id == current_user.id, WorkLog.date == today)
    ).order_by(WorkLog.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{log_id}", response_model=WorkLogResponse)
async def get_work_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WorkLog).options(selectinload(WorkLog.todo)).where(and_(WorkLog.id == log_id, WorkLog.user_id == current_user.id))
    )
    work_log = result.scalar_one_or_none()
    if not work_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工作日志不存在")
    return work_log


@router.put("/{log_id}", response_model=WorkLogResponse)
async def update_work_log(
    log_id: int,
    log_data: WorkLogUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WorkLog).where(and_(WorkLog.id == log_id, WorkLog.user_id == current_user.id))
    )
    work_log = result.scalar_one_or_none()
    if not work_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工作日志不存在")

    update_data = log_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(work_log, key, value)

    await db.commit()

    # 重新查询以加载关联的 todo
    result = await db.execute(
        select(WorkLog).options(selectinload(WorkLog.todo)).where(WorkLog.id == log_id)
    )
    return result.scalar_one()


@router.delete("/{log_id}")
async def delete_work_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WorkLog).where(and_(WorkLog.id == log_id, WorkLog.user_id == current_user.id))
    )
    work_log = result.scalar_one_or_none()
    if not work_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工作日志不存在")

    # 如果日志有关联任务且有进度更新，需要回退进度
    if work_log.todo_id and work_log.progress_update is not None:
        # 获取关联的任务
        todo_result = await db.execute(
            select(Todo).where(Todo.id == work_log.todo_id)
        )
        todo = todo_result.scalar_one_or_none()

        if todo:
            # 回退到创建日志前的进度
            new_progress = work_log.previous_progress if work_log.previous_progress is not None else 0
            todo.progress = new_progress

            # 根据进度自动设置状态
            if new_progress == 0:
                todo.status = "pending"
                todo.completed_at = None
            elif new_progress == 100:
                todo.status = "completed"
                if todo.completed_at is None:
                    todo.completed_at = datetime.utcnow()
            else:
                todo.status = "in_progress"
                todo.completed_at = None

    await db.delete(work_log)
    await db.commit()
    return {"message": "工作日志已删除"}
