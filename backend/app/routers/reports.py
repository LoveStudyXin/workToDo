from datetime import date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from pydantic import BaseModel
from datetime import datetime
import io

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.report import Report
from app.models.report_template import ReportTemplate
from app.services.report_generator import get_report_data, generate_report_content
from app.services.ai_service import ai_service
from app.services.presentation_generator import generate_presentation_html, get_available_styles

router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportGenerate(BaseModel):
    type: str  # daily/weekly/monthly/yearly
    start_date: date
    end_date: date
    template_id: Optional[int] = None
    use_ai: bool = False


class ReportResponse(BaseModel):
    id: int
    type: str
    start_date: date
    end_date: date
    raw_content: str
    ai_enhanced_content: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReportPreview(BaseModel):
    raw_content: str
    ai_enhanced_content: Optional[str] = None


def get_date_range(report_type: str, reference_date: date = None) -> tuple[date, date]:
    """Calculate date range based on report type"""
    if reference_date is None:
        reference_date = date.today()

    if report_type == "daily":
        return reference_date, reference_date
    elif report_type == "weekly":
        # Get Monday of the week
        start = reference_date - timedelta(days=reference_date.weekday())
        end = start + timedelta(days=6)
        return start, end
    elif report_type == "monthly":
        start = reference_date.replace(day=1)
        # Get last day of month
        if reference_date.month == 12:
            end = reference_date.replace(month=12, day=31)
        else:
            end = reference_date.replace(month=reference_date.month + 1, day=1) - timedelta(days=1)
        return start, end
    elif report_type == "yearly":
        start = reference_date.replace(month=1, day=1)
        end = reference_date.replace(month=12, day=31)
        return start, end
    else:
        return reference_date, reference_date


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    report_data: ReportGenerate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get template
    if report_data.template_id:
        result = await db.execute(
            select(ReportTemplate).where(
                and_(
                    ReportTemplate.id == report_data.template_id,
                    or_(
                        ReportTemplate.user_id == current_user.id,
                        ReportTemplate.user_id.is_(None)
                    )
                )
            )
        )
        template = result.scalar_one_or_none()
    else:
        # Get default template for type
        result = await db.execute(
            select(ReportTemplate).where(
                and_(
                    ReportTemplate.type == report_data.type,
                    ReportTemplate.is_default == True,
                    or_(
                        ReportTemplate.user_id == current_user.id,
                        ReportTemplate.user_id.is_(None)
                    )
                )
            ).order_by(ReportTemplate.user_id.desc()).limit(1)  # Prefer user template
        )
        template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在")

    # Get report data
    data = await get_report_data(
        db, current_user.id, report_data.start_date, report_data.end_date
    )

    # Generate raw content
    raw_content = generate_report_content(
        template.template_content,
        data,
        report_data.start_date,
        report_data.end_date
    )

    # AI enhancement if requested
    ai_enhanced_content = None
    if report_data.use_ai:
        ai_enhanced_content = await ai_service.enhance_report(raw_content, report_data.type)

    # Save report
    report = Report(
        user_id=current_user.id,
        type=report_data.type,
        start_date=report_data.start_date,
        end_date=report_data.end_date,
        raw_content=raw_content,
        ai_enhanced_content=ai_enhanced_content
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return report


@router.post("/preview", response_model=ReportPreview)
async def preview_report(
    report_data: ReportGenerate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Preview report without saving"""
    # Get template
    if report_data.template_id:
        result = await db.execute(
            select(ReportTemplate).where(
                and_(
                    ReportTemplate.id == report_data.template_id,
                    or_(
                        ReportTemplate.user_id == current_user.id,
                        ReportTemplate.user_id.is_(None)
                    )
                )
            )
        )
        template = result.scalar_one_or_none()
    else:
        result = await db.execute(
            select(ReportTemplate).where(
                and_(
                    ReportTemplate.type == report_data.type,
                    ReportTemplate.is_default == True,
                    or_(
                        ReportTemplate.user_id == current_user.id,
                        ReportTemplate.user_id.is_(None)
                    )
                )
            ).order_by(ReportTemplate.user_id.desc()).limit(1)
        )
        template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模板不存在")

    # Get report data
    data = await get_report_data(
        db, current_user.id, report_data.start_date, report_data.end_date
    )

    # Generate content
    raw_content = generate_report_content(
        template.template_content,
        data,
        report_data.start_date,
        report_data.end_date
    )

    # AI enhancement if requested
    ai_enhanced_content = None
    if report_data.use_ai:
        ai_enhanced_content = await ai_service.enhance_report(raw_content, report_data.type)

    return ReportPreview(raw_content=raw_content, ai_enhanced_content=ai_enhanced_content)


@router.get("", response_model=List[ReportResponse])
async def get_reports(
    type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Report).where(Report.user_id == current_user.id)

    if type:
        query = query.where(Report.type == type)
    if start_date:
        query = query.where(Report.start_date >= start_date)
    if end_date:
        query = query.where(Report.end_date <= end_date)

    query = query.order_by(Report.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Report).where(and_(Report.id == report_id, Report.user_id == current_user.id))
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")
    return report


@router.get("/{report_id}/export/markdown")
async def export_markdown(
    report_id: int,
    use_ai: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Report).where(and_(Report.id == report_id, Report.user_id == current_user.id))
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")

    content = report.ai_enhanced_content if use_ai and report.ai_enhanced_content else report.raw_content
    filename = f"report_{report.type}_{report.start_date}.md"

    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Report).where(and_(Report.id == report_id, Report.user_id == current_user.id))
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")

    await db.delete(report)
    await db.commit()
    return {"message": "报告已删除"}


# ========== 演示文稿相关接口 ==========

class PresentationGenerate(BaseModel):
    type: str  # daily/weekly/monthly/yearly
    start_date: date
    end_date: date
    style: str = "modern-dark"
    title: Optional[str] = None


@router.get("/presentation/styles")
async def get_presentation_styles():
    """获取可用的演示文稿风格列表"""
    return get_available_styles()


@router.post("/presentation/generate")
async def generate_presentation(
    data: PresentationGenerate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """直接生成演示文稿（不保存报告）"""
    # 获取报告数据
    report_data = await get_report_data(
        db, current_user.id, data.start_date, data.end_date
    )

    # 生成 HTML 演示
    html_content = generate_presentation_html(
        report_type=data.type,
        start_date=data.start_date,
        end_date=data.end_date,
        data=report_data,
        style=data.style,
        title=data.title
    )

    # 返回 HTML 文件
    filename = f"presentation_{data.type}_{data.start_date}.html"
    return StreamingResponse(
        io.BytesIO(html_content.encode("utf-8")),
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{report_id}/export/presentation")
async def export_presentation(
    report_id: int,
    style: str = Query("modern-dark"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """将已保存的报告导出为演示文稿"""
    # 获取报告
    result = await db.execute(
        select(Report).where(and_(Report.id == report_id, Report.user_id == current_user.id))
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")

    # 重新获取报告数据用于生成演示
    report_data = await get_report_data(
        db, current_user.id, report.start_date, report.end_date
    )

    # 生成 HTML 演示
    html_content = generate_presentation_html(
        report_type=report.type,
        start_date=report.start_date,
        end_date=report.end_date,
        data=report_data,
        style=style
    )

    # 返回 HTML 文件
    filename = f"presentation_{report.type}_{report.start_date}.html"
    return StreamingResponse(
        io.BytesIO(html_content.encode("utf-8")),
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
