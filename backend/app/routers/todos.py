from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.todo import Todo

router = APIRouter(prefix="/api/todos", tags=["todos"])


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "其他"
    priority: int = 3
    estimated_hours: Optional[float] = None
    due_date: Optional[date] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    progress: Optional[int] = None
    due_date: Optional[date] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: str
    priority: int
    status: str
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    progress: int
    due_date: Optional[date]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=TodoResponse)
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    todo = Todo(
        user_id=current_user.id,
        title=todo_data.title,
        description=todo_data.description,
        category=todo_data.category,
        priority=todo_data.priority,
        estimated_hours=todo_data.estimated_hours,
        due_date=todo_data.due_date
    )
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo


@router.get("", response_model=List[TodoResponse])
async def get_todos(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[int] = Query(None),
    due_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if status:
        query = query.where(Todo.status == status)
    if category:
        query = query.where(Todo.category == category)
    if priority:
        query = query.where(Todo.priority == priority)
    if due_date:
        query = query.where(Todo.due_date == due_date)

    query = query.order_by(Todo.priority.desc(), Todo.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/today", response_model=List[TodoResponse])
async def get_today_todos(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    今日任务：
    1. 截止日期 <= 今天 且 未完成（今天到期 + 已逾期）
    2. 或 状态为进行中（不管截止日期）
    """
    today = date.today()
    query = select(Todo).where(
        and_(
            Todo.user_id == current_user.id,
            Todo.status != "completed",
            or_(
                Todo.due_date <= today,  # 今天到期或已逾期
                Todo.status == "in_progress"  # 进行中的任务
            )
        )
    ).order_by(Todo.priority.desc(), Todo.due_date.asc(), Todo.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Todo).where(and_(Todo.id == todo_id, Todo.user_id == current_user.id))
    )
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Todo).where(and_(Todo.id == todo_id, Todo.user_id == current_user.id))
    )
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    update_data = todo_data.model_dump(exclude_unset=True)

    # 根据进度自动设置状态
    if "progress" in update_data:
        progress = update_data["progress"]
        if progress == 0:
            update_data["status"] = "pending"
            update_data["completed_at"] = None
        elif progress == 100:
            update_data["status"] = "completed"
            if todo.status != "completed":
                update_data["completed_at"] = datetime.utcnow()
        else:  # 1-99%
            update_data["status"] = "in_progress"
            update_data["completed_at"] = None

    # 兼容直接设置状态的情况
    elif "status" in update_data:
        if update_data["status"] == "completed" and todo.status != "completed":
            update_data["completed_at"] = datetime.utcnow()
            update_data["progress"] = 100
        elif update_data["status"] == "pending":
            update_data["progress"] = 0
            update_data["completed_at"] = None

    for key, value in update_data.items():
        setattr(todo, key, value)

    await db.commit()
    await db.refresh(todo)
    return todo


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Todo).where(and_(Todo.id == todo_id, Todo.user_id == current_user.id))
    )
    todo = result.scalar_one_or_none()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    await db.delete(todo)
    await db.commit()
    return {"message": "任务已删除"}
