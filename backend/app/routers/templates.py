from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.report_template import ReportTemplate
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/templates", tags=["templates"])


# Default templates
DEFAULT_TEMPLATES = [
    {
        "name": "日报模板",
        "type": "daily",
        "template_content": """# {{date_range}} 工作日报

## 今日完成

{{completed_tasks}}

## 进行中

{{in_progress_tasks}}

## 工作时长

今日工作: {{total_hours}} 小时

## 遇到的问题

{{issues}}

## 明日计划

{{next_plans}}
""",
        "is_default": True
    },
    {
        "name": "周报模板",
        "type": "weekly",
        "template_content": """# {{date_range}} 工作周报

## 本周完成

{{completed_tasks}}

## 进行中的工作

{{in_progress_tasks}}

## 工作量统计

- 总工时: {{total_hours}} 小时
- 完成任务数: {{completed_count}}
- 进行中任务: {{in_progress_count}}

## 本周亮点

{{highlights}}

## 遇到的问题

{{issues}}

## 下周计划

{{next_plans}}
""",
        "is_default": True
    },
    {
        "name": "月报模板",
        "type": "monthly",
        "template_content": """# {{date_range}} 工作月报

## 月度工作概览

{{completed_tasks}}

## 分类统计

{{category_stats}}

## 关键成果

{{highlights}}

## 问题与改进

{{issues}}

## 下月计划

{{next_plans}}
""",
        "is_default": True
    },
    {
        "name": "年度绩效报告模板",
        "type": "yearly",
        "template_content": """# {{date_range}} 年度绩效报告

## 年度工作总结

### 完成任务统计
- 总完成任务数: {{completed_count}}
- 总工作时长: {{total_hours}} 小时

### 分类工作量

{{category_stats}}

## 重点项目与成果

{{highlights}}

## 技能成长

{{skill_growth}}

## 改进与反思

{{issues}}

## 来年规划

{{next_plans}}
""",
        "is_default": True
    }
]


class TemplateCreate(BaseModel):
    name: str
    type: str  # daily/weekly/monthly/yearly
    template_content: str
    is_default: bool = False


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_content: Optional[str] = None
    is_default: Optional[bool] = None


class AIGenerateRequest(BaseModel):
    user_input: str
    template_type: str  # daily/weekly/monthly/yearly
    mode: str  # describe or convert


class TemplateResponse(BaseModel):
    id: int
    user_id: Optional[int]
    name: str
    type: str
    template_content: str
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/init-defaults")
async def init_default_templates(
    db: AsyncSession = Depends(get_db)
):
    """Initialize system default templates (no user_id)"""
    # Check if defaults already exist
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.user_id.is_(None))
    )
    existing = result.scalars().all()
    if existing:
        return {"message": "默认模板已存在", "count": len(existing)}

    for template_data in DEFAULT_TEMPLATES:
        template = ReportTemplate(
            user_id=None,
            **template_data
        )
        db.add(template)

    await db.commit()
    return {"message": "默认模板初始化成功", "count": len(DEFAULT_TEMPLATES)}


@router.post("", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    template = ReportTemplate(
        user_id=current_user.id,
        name=template_data.name,
        type=template_data.type,
        template_content=template_data.template_content,
        is_default=template_data.is_default
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.get("", response_model=List[TemplateResponse])
async def get_templates(
    type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get both user templates and system templates (user_id = None)
    query = select(ReportTemplate).where(
        or_(
            ReportTemplate.user_id == current_user.id,
            ReportTemplate.user_id.is_(None)
        )
    )

    if type:
        query = query.where(ReportTemplate.type == type)

    query = query.order_by(ReportTemplate.is_default.desc(), ReportTemplate.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ReportTemplate).where(
            and_(
                ReportTemplate.id == template_id,
                or_(
                    ReportTemplate.user_id == current_user.id,
                    ReportTemplate.user_id.is_(None)
                )
            )
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在")
    return template


@router.post("/generate-ai")
async def generate_template_with_ai(
    request: AIGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate template content using AI"""
    if not request.user_input.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入内容"
        )

    if request.mode not in ["describe", "convert"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的模式"
        )

    result = await ai_service.generate_template(
        user_input=request.user_input,
        template_type=request.template_type,
        mode=request.mode
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI生成失败，请检查AI服务配置"
        )

    return {"template_content": result}


@router.post("/{template_id}/copy", response_model=TemplateResponse)
async def copy_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """复制模板到当前用户名下"""
    # 查找原模板（可以是系统模板或用户自己的模板）
    result = await db.execute(
        select(ReportTemplate).where(
            and_(
                ReportTemplate.id == template_id,
                or_(
                    ReportTemplate.user_id == current_user.id,
                    ReportTemplate.user_id.is_(None)
                )
            )
        )
    )
    source_template = result.scalar_one_or_none()
    if not source_template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在")

    # 创建副本
    new_template = ReportTemplate(
        user_id=current_user.id,
        name=f"{source_template.name}（副本）",
        type=source_template.type,
        template_content=source_template.template_content,
        is_default=False
    )
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    return new_template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Only allow updating user's own templates
    result = await db.execute(
        select(ReportTemplate).where(
            and_(
                ReportTemplate.id == template_id,
                ReportTemplate.user_id == current_user.id
            )
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在或无权修改")

    update_data = template_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)

    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Only allow deleting user's own templates
    result = await db.execute(
        select(ReportTemplate).where(
            and_(
                ReportTemplate.id == template_id,
                ReportTemplate.user_id == current_user.id
            )
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在或无权删除")

    await db.delete(template)
    await db.commit()
    return {"message": "模板已删除"}
