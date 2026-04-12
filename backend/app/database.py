from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# 默认报告模板
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


async def init_db():
    """初始化数据库：创建表并添加默认数据"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 初始化默认模板
    await init_default_templates()


async def init_default_templates():
    """如果不存在默认模板，则创建"""
    from app.models.report_template import ReportTemplate

    async with async_session() as session:
        # 检查是否已有系统默认模板
        result = await session.execute(
            select(ReportTemplate).where(ReportTemplate.user_id.is_(None)).limit(1)
        )
        existing = result.scalar_one_or_none()

        if existing:
            return  # 已有默认模板，跳过

        # 创建默认模板
        for template_data in DEFAULT_TEMPLATES:
            template = ReportTemplate(
                user_id=None,
                **template_data
            )
            session.add(template)

        await session.commit()
        print("默认报告模板已初始化")
