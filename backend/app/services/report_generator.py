from datetime import date, timedelta
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.todo import Todo
from app.models.work_log import WorkLog


async def get_report_data(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """Gather all data needed for report generation"""

    # Get completed tasks in date range
    completed_result = await db.execute(
        select(Todo).where(
            and_(
                Todo.user_id == user_id,
                Todo.status == "completed",
                Todo.completed_at >= start_date,
                Todo.completed_at <= end_date + timedelta(days=1)
            )
        ).order_by(Todo.completed_at.desc())
    )
    completed_tasks = completed_result.scalars().all()

    # Get in-progress tasks
    in_progress_result = await db.execute(
        select(Todo).where(
            and_(
                Todo.user_id == user_id,
                Todo.status == "in_progress"
            )
        ).order_by(Todo.priority.desc())
    )
    in_progress_tasks = in_progress_result.scalars().all()

    # Get pending tasks (for next plans)
    pending_result = await db.execute(
        select(Todo).where(
            and_(
                Todo.user_id == user_id,
                Todo.status == "pending"
            )
        ).order_by(Todo.priority.desc(), Todo.due_date.asc())
    )
    pending_tasks = pending_result.scalars().all()

    # Get work logs in date range
    logs_result = await db.execute(
        select(WorkLog).where(
            and_(
                WorkLog.user_id == user_id,
                WorkLog.date >= start_date,
                WorkLog.date <= end_date
            )
        ).order_by(WorkLog.date.desc())
    )
    work_logs = logs_result.scalars().all()

    # Calculate statistics
    total_hours = sum(log.hours_spent for log in work_logs)

    # Category statistics
    category_stats = {}
    for task in completed_tasks:
        if task.category not in category_stats:
            category_stats[task.category] = {"count": 0, "hours": 0}
        category_stats[task.category]["count"] += 1
        category_stats[task.category]["hours"] += task.actual_hours or 0

    # Extract issues from work logs
    issues = [log.notes for log in work_logs if log.notes]

    return {
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "pending_tasks": pending_tasks,
        "work_logs": work_logs,
        "total_hours": round(total_hours, 1),
        "completed_count": len(completed_tasks),
        "in_progress_count": len(in_progress_tasks),
        "category_stats": category_stats,
        "issues": issues
    }


def format_task_list(tasks: List[Todo]) -> str:
    """Format task list as markdown"""
    if not tasks:
        return "- 无"

    lines = []
    for task in tasks:
        priority_emoji = "🔴" if task.priority >= 4 else "🟡" if task.priority >= 3 else "🟢"
        progress_str = f" ({task.progress}%)" if task.progress < 100 else ""
        hours_str = f" [{task.actual_hours or 0}h]" if task.actual_hours else ""
        lines.append(f"- {priority_emoji} [{task.category}] {task.title}{progress_str}{hours_str}")

    return "\n".join(lines)


def format_category_stats(stats: Dict[str, Dict]) -> str:
    """Format category statistics as markdown"""
    if not stats:
        return "- 无数据"

    lines = []
    for category, data in stats.items():
        lines.append(f"- {category}: {data['count']} 个任务, {data['hours']}h")

    return "\n".join(lines)


def generate_report_content(
    template_content: str,
    data: Dict[str, Any],
    start_date: date,
    end_date: date
) -> str:
    """Fill template with actual data"""

    # Format date range
    if start_date == end_date:
        date_range = start_date.strftime("%Y-%m-%d")
    else:
        date_range = f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"

    # Replace placeholders
    content = template_content
    content = content.replace("{{date_range}}", date_range)
    content = content.replace("{{completed_tasks}}", format_task_list(data["completed_tasks"]))
    content = content.replace("{{in_progress_tasks}}", format_task_list(data["in_progress_tasks"]))
    content = content.replace("{{total_hours}}", str(data["total_hours"]))
    content = content.replace("{{completed_count}}", str(data["completed_count"]))
    content = content.replace("{{in_progress_count}}", str(data["in_progress_count"]))
    content = content.replace("{{category_stats}}", format_category_stats(data["category_stats"]))

    # Issues
    issues_text = "\n".join(f"- {issue}" for issue in data["issues"]) if data["issues"] else "- 无"
    content = content.replace("{{issues}}", issues_text)

    # Next plans (from pending and in-progress tasks)
    next_tasks = data["pending_tasks"][:5] + data["in_progress_tasks"][:5]
    content = content.replace("{{next_plans}}", format_task_list(next_tasks[:5]))

    # Highlights (top completed tasks by priority)
    highlights = sorted(data["completed_tasks"], key=lambda x: x.priority, reverse=True)[:5]
    content = content.replace("{{highlights}}", format_task_list(highlights))

    # Skill growth placeholder
    content = content.replace("{{skill_growth}}", "- 根据工作内容总结技能成长")

    return content
