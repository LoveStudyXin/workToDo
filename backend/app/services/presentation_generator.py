"""
演示文稿生成服务
将报告数据转换为 HTML 幻灯片演示
整合自 frontend-slides 项目的风格预设和动画效果
"""
from datetime import date
from typing import Dict, Any, List, Optional
from app.models.todo import Todo


# 报告类型中文映射
REPORT_TYPE_NAMES = {
    "daily": "日报",
    "weekly": "周报",
    "monthly": "月报",
    "yearly": "年度报告"
}

# 12 种演示风格（来自 frontend-slides STYLE_PRESETS.md）
PRESENTATION_STYLES = {
    # === 深色主题 ===
    "bold-signal": {
        "name": "Bold Signal",
        "name_cn": "大胆信号",
        "vibe": "自信、大胆、现代、高冲击力",
        "bg_primary": "#1a1a1a",
        "bg_secondary": "#2d2d2d",
        "bg_gradient": "linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)",
        "text_primary": "#ffffff",
        "text_secondary": "#b0b0b0",
        "accent": "#FF5722",
        "accent_secondary": "#ff7043",
        "font_display": "'Archivo Black', sans-serif",
        "font_body": "'Space Grotesk', sans-serif",
        "font_import": "https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@400;500;600&display=swap",
    },
    "electric-studio": {
        "name": "Electric Studio",
        "name_cn": "电力工作室",
        "vibe": "大胆、干净、专业、高对比度",
        "bg_primary": "#0a0a0a",
        "bg_secondary": "#111111",
        "bg_gradient": "linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%)",
        "text_primary": "#ffffff",
        "text_secondary": "#888888",
        "accent": "#4361ee",
        "accent_secondary": "#7c3aed",
        "font_display": "'Manrope', sans-serif",
        "font_body": "'Manrope', sans-serif",
        "font_import": "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;800&display=swap",
    },
    "creative-voltage": {
        "name": "Creative Voltage",
        "name_cn": "创意电压",
        "vibe": "大胆、创意、充满活力、复古现代",
        "bg_primary": "#1a1a2e",
        "bg_secondary": "#0f0f1a",
        "bg_gradient": "linear-gradient(135deg, #0066ff 0%, #1a1a2e 50%)",
        "text_primary": "#ffffff",
        "text_secondary": "#9ca3af",
        "accent": "#0066ff",
        "accent_secondary": "#d4ff00",
        "font_display": "'Syne', sans-serif",
        "font_body": "'Space Mono', monospace",
        "font_import": "https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Space+Mono:wght@400;700&display=swap",
    },
    "dark-botanical": {
        "name": "Dark Botanical",
        "name_cn": "暗夜植物",
        "vibe": "优雅、精致、艺术、高端",
        "bg_primary": "#0f0f0f",
        "bg_secondary": "#1a1a1a",
        "bg_gradient": "linear-gradient(135deg, #0f0f0f 0%, #1a1515 100%)",
        "text_primary": "#e8e4df",
        "text_secondary": "#9a9590",
        "accent": "#d4a574",
        "accent_secondary": "#e8b4b8",
        "font_display": "'Cormorant', serif",
        "font_body": "'IBM Plex Sans', sans-serif",
        "font_import": "https://fonts.googleapis.com/css2?family=Cormorant:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500&display=swap",
    },
    # === 浅色主题 ===
    "notebook-tabs": {
        "name": "Notebook Tabs",
        "name_cn": "笔记标签",
        "vibe": "社论风、有组织、优雅、触感",
        "bg_primary": "#2d2d2d",
        "bg_secondary": "#f8f6f1",
        "bg_gradient": "linear-gradient(135deg, #2d2d2d 0%, #3d3d3d 100%)",
        "text_primary": "#1a1a1a",
        "text_secondary": "#666666",
        "accent": "#98d4bb",
        "accent_secondary": "#c7b8ea",
        "font_display": "'Bodoni Moda', serif",
        "font_body": "'DM Sans', sans-serif",
        "font_import": "https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@400;700&family=DM+Sans:wght@400;500&display=swap",
        "is_light": True,
    },
    "pastel-geometry": {
        "name": "Pastel Geometry",
        "name_cn": "柔和几何",
        "vibe": "友好、有组织、现代、平易近人",
        "bg_primary": "#c8d9e6",
        "bg_secondary": "#faf9f7",
        "bg_gradient": "linear-gradient(135deg, #c8d9e6 0%, #e8f0f5 100%)",
        "text_primary": "#1a1a1a",
        "text_secondary": "#555555",
        "accent": "#5a7c6a",
        "accent_secondary": "#f0b4d4",
        "font_display": "'Plus Jakarta Sans', sans-serif",
        "font_body": "'Plus Jakarta Sans', sans-serif",
        "font_import": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap",
        "is_light": True,
    },
    "split-pastel": {
        "name": "Split Pastel",
        "name_cn": "分割柔彩",
        "vibe": "俏皮、现代、友好、创意",
        "bg_primary": "#f5e6dc",
        "bg_secondary": "#e4dff0",
        "bg_gradient": "linear-gradient(90deg, #f5e6dc 50%, #e4dff0 50%)",
        "text_primary": "#1a1a1a",
        "text_secondary": "#555555",
        "accent": "#7c6aad",
        "accent_secondary": "#c8f0d8",
        "font_display": "'Outfit', sans-serif",
        "font_body": "'Outfit', sans-serif",
        "font_import": "https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700;800&display=swap",
        "is_light": True,
    },
    "vintage-editorial": {
        "name": "Vintage Editorial",
        "name_cn": "复古编辑",
        "vibe": "机智、自信、编辑风、个性化",
        "bg_primary": "#f5f3ee",
        "bg_secondary": "#ebe8e0",
        "bg_gradient": "linear-gradient(135deg, #f5f3ee 0%, #ebe8e0 100%)",
        "text_primary": "#1a1a1a",
        "text_secondary": "#555555",
        "accent": "#c41e3a",
        "accent_secondary": "#e8d4c0",
        "font_display": "'Fraunces', serif",
        "font_body": "'Work Sans', sans-serif",
        "font_import": "https://fonts.googleapis.com/css2?family=Fraunces:wght@700;900&family=Work+Sans:wght@400;500&display=swap",
        "is_light": True,
    },
    # === 特色主题 ===
    "neon-cyber": {
        "name": "Neon Cyber",
        "name_cn": "霓虹赛博",
        "vibe": "未来感、科技感、自信",
        "bg_primary": "#0a0f1c",
        "bg_secondary": "#111827",
        "bg_gradient": "linear-gradient(135deg, #0a0f1c 0%, #1a1030 50%, #0a0f1c 100%)",
        "text_primary": "#ffffff",
        "text_secondary": "#94a3b8",
        "accent": "#00ffcc",
        "accent_secondary": "#ff00aa",
        "font_display": "'Clash Display', sans-serif",
        "font_body": "'Satoshi', sans-serif",
        "font_import": "https://api.fontshare.com/v2/css?f[]=clash-display@700&f[]=satoshi@400;500&display=swap",
    },
    "terminal-green": {
        "name": "Terminal Green",
        "name_cn": "终端绿",
        "vibe": "开发者风格、黑客美学",
        "bg_primary": "#0d1117",
        "bg_secondary": "#161b22",
        "bg_gradient": "linear-gradient(180deg, #0d1117 0%, #161b22 100%)",
        "text_primary": "#39d353",
        "text_secondary": "#7d8590",
        "accent": "#39d353",
        "accent_secondary": "#58a6ff",
        "font_display": "'JetBrains Mono', monospace",
        "font_body": "'JetBrains Mono', monospace",
        "font_import": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap",
    },
    "swiss-modern": {
        "name": "Swiss Modern",
        "name_cn": "瑞士现代",
        "vibe": "干净、精确、包豪斯风格",
        "bg_primary": "#ffffff",
        "bg_secondary": "#f5f5f5",
        "bg_gradient": "linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%)",
        "text_primary": "#000000",
        "text_secondary": "#666666",
        "accent": "#ff3300",
        "accent_secondary": "#0066ff",
        "font_display": "'Archivo', sans-serif",
        "font_body": "'Nunito', sans-serif",
        "font_import": "https://fonts.googleapis.com/css2?family=Archivo:wght@800&family=Nunito:wght@400;500&display=swap",
        "is_light": True,
    },
    "paper-ink": {
        "name": "Paper & Ink",
        "name_cn": "纸墨风",
        "vibe": "编辑风、文学感、深思熟虑",
        "bg_primary": "#faf9f7",
        "bg_secondary": "#f0ece4",
        "bg_gradient": "linear-gradient(135deg, #faf9f7 0%, #f5f2eb 100%)",
        "text_primary": "#1a1a1a",
        "text_secondary": "#666666",
        "accent": "#c41e3a",
        "accent_secondary": "#1a1a1a",
        "font_display": "'Cormorant Garamond', serif",
        "font_body": "'Source Serif 4', serif",
        "font_import": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600&family=Source+Serif+4:wght@400;500&display=swap",
        "is_light": True,
    },
}


def _format_task_for_slide(task: Todo) -> Dict[str, Any]:
    """格式化单个任务用于幻灯片显示"""
    priority_colors = {5: "#ef4444", 4: "#f97316", 3: "#eab308", 2: "#22c55e", 1: "#64748b"}
    return {
        "title": task.title,
        "category": task.category or "未分类",
        "priority": task.priority,
        "priority_color": priority_colors.get(task.priority, "#64748b"),
        "progress": task.progress,
        "hours": task.actual_hours or 0,
        "estimated_hours": task.estimated_hours or 0
    }


def _chunk_list(lst: List, size: int) -> List[List]:
    """将列表分割成固定大小的块"""
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def generate_presentation_html(
    report_type: str,
    start_date: date,
    end_date: date,
    data: Dict[str, Any],
    style: str = "neon-cyber",
    title: Optional[str] = None
) -> str:
    """
    生成 HTML 演示文稿

    Args:
        report_type: 报告类型 (daily/weekly/monthly/yearly)
        start_date: 开始日期
        end_date: 结束日期
        data: 报告数据 (来自 get_report_data)
        style: 演示风格
        title: 自定义标题

    Returns:
        完整的 HTML 字符串
    """
    # 获取风格配置
    style_config = PRESENTATION_STYLES.get(style, PRESENTATION_STYLES["neon-cyber"])

    # 格式化日期范围
    if start_date == end_date:
        date_range = start_date.strftime("%Y年%m月%d日")
    else:
        date_range = f"{start_date.strftime('%Y.%m.%d')} - {end_date.strftime('%Y.%m.%d')}"

    # 默认标题
    if not title:
        title = f"{REPORT_TYPE_NAMES.get(report_type, '工作报告')}"

    # 构建幻灯片内容
    slides = []

    # 1. 标题页
    slides.append(_generate_title_slide(title, date_range, style_config))

    # 2. 数据概览页
    slides.append(_generate_overview_slide(data, style_config))

    # 3. 已完成任务页（每页最多5个）
    completed_tasks = data.get("completed_tasks", [])
    if completed_tasks:
        task_chunks = _chunk_list(completed_tasks, 5)
        for i, chunk in enumerate(task_chunks):
            page_title = "已完成任务" if len(task_chunks) == 1 else f"已完成任务 ({i+1}/{len(task_chunks)})"
            slides.append(_generate_tasks_slide(page_title, chunk, "completed", style_config))

    # 4. 进行中任务页
    in_progress_tasks = data.get("in_progress_tasks", [])
    if in_progress_tasks:
        task_chunks = _chunk_list(in_progress_tasks, 5)
        for i, chunk in enumerate(task_chunks):
            page_title = "进行中任务" if len(task_chunks) == 1 else f"进行中任务 ({i+1}/{len(task_chunks)})"
            slides.append(_generate_tasks_slide(page_title, chunk, "in_progress", style_config))

    # 5. 分类统计页
    category_stats = data.get("category_stats", {})
    if category_stats:
        slides.append(_generate_category_slide(category_stats, style_config))

    # 6. 下一步计划页
    pending_tasks = data.get("pending_tasks", [])[:5]
    if pending_tasks or in_progress_tasks:
        next_tasks = (in_progress_tasks[:3] + pending_tasks[:3])[:5]
        if next_tasks:
            slides.append(_generate_next_plans_slide(next_tasks, style_config))

    # 7. 结束页
    slides.append(_generate_end_slide(data, style_config))

    # 生成完整 HTML
    return _generate_full_html(slides, style_config, title)


def _generate_title_slide(title: str, date_range: str, style: Dict) -> str:
    """生成标题幻灯片"""
    return f'''
    <section class="slide title-slide">
        <div class="slide-bg-effect"></div>
        <div class="slide-content">
            <h1 class="reveal">{title}</h1>
            <p class="subtitle reveal" style="transition-delay: 0.1s">{date_range}</p>
            <div class="scroll-hint reveal" style="transition-delay: 0.3s">
                <span>向下滚动或按空格键</span>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 5v14M19 12l-7 7-7-7"/>
                </svg>
            </div>
        </div>
    </section>
    '''


def _generate_overview_slide(data: Dict[str, Any], style: Dict) -> str:
    """生成数据概览幻灯片"""
    completed = data.get("completed_count", 0)
    in_progress = data.get("in_progress_count", 0)
    total_hours = data.get("total_hours", 0)
    categories = len(data.get("category_stats", {}))

    return f'''
    <section class="slide">
        <div class="slide-content">
            <h2 class="reveal">数据概览</h2>
            <div class="stats-grid">
                <div class="stat-card reveal" style="transition-delay: 0.1s">
                    <div class="stat-icon">✓</div>
                    <div class="stat-number">{completed}</div>
                    <div class="stat-label">已完成任务</div>
                </div>
                <div class="stat-card reveal" style="transition-delay: 0.15s">
                    <div class="stat-icon">⟳</div>
                    <div class="stat-number">{in_progress}</div>
                    <div class="stat-label">进行中任务</div>
                </div>
                <div class="stat-card reveal" style="transition-delay: 0.2s">
                    <div class="stat-icon">⏱</div>
                    <div class="stat-number">{total_hours}<span class="stat-unit">h</span></div>
                    <div class="stat-label">投入时间</div>
                </div>
                <div class="stat-card reveal" style="transition-delay: 0.25s">
                    <div class="stat-icon">◈</div>
                    <div class="stat-number">{categories}</div>
                    <div class="stat-label">任务分类</div>
                </div>
            </div>
        </div>
    </section>
    '''


def _generate_tasks_slide(title: str, tasks: List[Todo], task_type: str, style: Dict) -> str:
    """生成任务列表幻灯片"""
    task_items = []
    for i, task in enumerate(tasks):
        t = _format_task_for_slide(task)
        progress_bar = ""
        if task_type == "in_progress":
            progress_bar = f'''
                <div class="task-progress-bar">
                    <div class="task-progress-fill" style="width: {t['progress']}%"></div>
                    <span class="task-progress-text">{t['progress']}%</span>
                </div>
            '''

        task_items.append(f'''
            <div class="task-card reveal" style="transition-delay: {0.1 + i * 0.05}s">
                <div class="task-header">
                    <span class="task-category">{t['category']}</span>
                    <span class="task-hours">{t['hours']}h</span>
                </div>
                <div class="task-title">{t['title']}</div>
                {progress_bar}
            </div>
        ''')

    return f'''
    <section class="slide">
        <div class="slide-content">
            <h2 class="reveal">{title}</h2>
            <div class="tasks-list">
                {''.join(task_items)}
            </div>
        </div>
    </section>
    '''


def _generate_category_slide(category_stats: Dict[str, Dict], style: Dict) -> str:
    """生成分类统计幻灯片"""
    total_count = sum(cat["count"] for cat in category_stats.values())
    total_hours = sum(cat["hours"] for cat in category_stats.values())

    colors = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"]

    category_items = []
    for i, (category, stats) in enumerate(category_stats.items()):
        color = colors[i % len(colors)]
        percent = round(stats["count"] / total_count * 100) if total_count > 0 else 0
        category_items.append(f'''
            <div class="category-item reveal" style="transition-delay: {0.1 + i * 0.05}s">
                <div class="category-bar-container">
                    <div class="category-bar" style="width: {percent}%; background: {color}"></div>
                </div>
                <div class="category-info">
                    <span class="category-name">{category}</span>
                    <span class="category-stats">{stats['count']} 任务 · {stats['hours']}h</span>
                </div>
            </div>
        ''')

    return f'''
    <section class="slide">
        <div class="slide-content">
            <h2 class="reveal">分类统计</h2>
            <div class="category-chart">
                {''.join(category_items)}
            </div>
            <div class="category-summary reveal" style="transition-delay: 0.3s">
                共 <strong>{total_count}</strong> 个任务，投入 <strong>{round(total_hours, 1)}</strong> 小时
            </div>
        </div>
    </section>
    '''


def _generate_next_plans_slide(tasks: List[Todo], style: Dict) -> str:
    """生成下一步计划幻灯片"""
    plan_items = []
    for i, task in enumerate(tasks):
        t = _format_task_for_slide(task)
        plan_items.append(f'''
            <div class="plan-item reveal" style="transition-delay: {0.1 + i * 0.08}s">
                <div class="plan-number">{i + 1:02d}</div>
                <div class="plan-content">
                    <div class="plan-title">{t['title']}</div>
                    <div class="plan-meta">{t['category']} · 预计 {t['estimated_hours'] or '?'}h</div>
                </div>
            </div>
        ''')

    return f'''
    <section class="slide">
        <div class="slide-content">
            <h2 class="reveal">下一步计划</h2>
            <div class="plans-list">
                {''.join(plan_items)}
            </div>
        </div>
    </section>
    '''


def _generate_end_slide(data: Dict[str, Any], style: Dict) -> str:
    """生成结束幻灯片"""
    completed = data.get("completed_count", 0)
    hours = data.get("total_hours", 0)

    return f'''
    <section class="slide end-slide">
        <div class="slide-bg-effect"></div>
        <div class="slide-content">
            <div class="end-icon reveal">🎯</div>
            <h2 class="reveal" style="transition-delay: 0.1s">本期总结</h2>
            <p class="end-summary reveal" style="transition-delay: 0.2s">
                完成 <strong>{completed}</strong> 项任务<br>
                投入 <strong>{hours}</strong> 小时
            </p>
            <p class="end-message reveal" style="transition-delay: 0.3s">继续保持，加油！</p>
        </div>
    </section>
    '''


def _generate_full_html(slides: List[str], style: Dict, title: str) -> str:
    """生成完整的 HTML 文档"""
    slides_html = "\n".join(slides)
    is_light = style.get("is_light", False)

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="{style['font_import']}" rel="stylesheet">
    <style>
        /* ==========================================
           CSS 变量 - 主题配置
           ========================================== */
        :root {{
            --bg-primary: {style['bg_primary']};
            --bg-secondary: {style['bg_secondary']};
            --bg-gradient: {style['bg_gradient']};
            --text-primary: {style['text_primary']};
            --text-secondary: {style['text_secondary']};
            --accent: {style['accent']};
            --accent-secondary: {style['accent_secondary']};
            --font-display: {style['font_display']};
            --font-body: {style['font_body']};

            /* 响应式排版 */
            --title-size: clamp(2rem, 6vw, 4.5rem);
            --h2-size: clamp(1.5rem, 4vw, 2.5rem);
            --body-size: clamp(0.875rem, 1.5vw, 1.125rem);
            --small-size: clamp(0.75rem, 1vw, 0.875rem);

            /* 响应式间距 */
            --slide-padding: clamp(1.5rem, 5vw, 5rem);
            --content-gap: clamp(1rem, 3vw, 2.5rem);
            --element-gap: clamp(0.5rem, 1.5vw, 1rem);

            /* 动画缓动 */
            --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
            --ease-out-back: cubic-bezier(0.34, 1.56, 0.64, 1);
        }}

        /* ==========================================
           基础重置 & 滚动吸附
           ========================================== */
        *, *::before, *::after {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            scroll-snap-type: y mandatory;
            scroll-behavior: smooth;
            height: 100%;
            overflow-x: hidden;
        }}

        body {{
            font-family: var(--font-body);
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            height: 100%;
            overflow-x: hidden;
        }}

        /* ==========================================
           幻灯片基础结构
           ========================================== */
        .slide {{
            width: 100vw;
            height: 100vh;
            height: 100dvh;
            overflow: hidden;
            scroll-snap-align: start;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            background: var(--bg-gradient);
        }}

        .slide-content {{
            width: 100%;
            max-width: 1100px;
            padding: var(--slide-padding);
            z-index: 1;
        }}

        /* 背景效果层 */
        .slide-bg-effect {{
            position: absolute;
            inset: 0;
            pointer-events: none;
            overflow: hidden;
        }}

        .title-slide .slide-bg-effect::before,
        .end-slide .slide-bg-effect::before {{
            content: '';
            position: absolute;
            width: 150%;
            height: 150%;
            top: -25%;
            left: -25%;
            background: radial-gradient(ellipse at 30% 70%, {"rgba(255,255,255,0.03)" if not is_light else "rgba(0,0,0,0.02)"} 0%, transparent 50%),
                        radial-gradient(ellipse at 70% 30%, var(--accent) 0%, transparent 40%);
            opacity: 0.15;
            animation: bgFloat 20s ease-in-out infinite;
        }}

        @keyframes bgFloat {{
            0%, 100% {{ transform: translate(0, 0) rotate(0deg); }}
            50% {{ transform: translate(-5%, 5%) rotate(3deg); }}
        }}

        /* ==========================================
           标题幻灯片
           ========================================== */
        .title-slide {{
            text-align: center;
        }}

        .title-slide h1 {{
            font-family: var(--font-display);
            font-size: var(--title-size);
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .subtitle {{
            font-size: clamp(1rem, 2.5vw, 1.5rem);
            color: var(--text-secondary);
            margin-bottom: 3rem;
            letter-spacing: 0.05em;
        }}

        .scroll-hint {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.75rem;
            color: var(--text-secondary);
            font-size: var(--small-size);
            animation: bounce 2s ease-in-out infinite;
        }}

        .scroll-hint svg {{
            opacity: 0.6;
        }}

        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(8px); }}
        }}

        /* ==========================================
           标题样式
           ========================================== */
        h2 {{
            font-family: var(--font-display);
            font-size: var(--h2-size);
            font-weight: 600;
            margin-bottom: var(--content-gap);
            color: var(--text-primary);
            position: relative;
        }}

        h2::after {{
            content: '';
            position: absolute;
            bottom: -0.5rem;
            left: 0;
            width: 3rem;
            height: 3px;
            background: var(--accent);
            border-radius: 2px;
        }}

        /* ==========================================
           统计卡片
           ========================================== */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--element-gap);
            margin-top: var(--content-gap);
        }}

        .stat-card {{
            background: {"rgba(255,255,255,0.03)" if not is_light else "rgba(0,0,0,0.03)"};
            border: 1px solid {"rgba(255,255,255,0.08)" if not is_light else "rgba(0,0,0,0.08)"};
            border-radius: 16px;
            padding: clamp(1.25rem, 3vw, 2rem);
            text-align: center;
            transition: transform 0.4s var(--ease-out-expo), box-shadow 0.4s var(--ease-out-expo);
        }}

        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 40px {"rgba(0,0,0,0.3)" if not is_light else "rgba(0,0,0,0.1)"};
        }}

        .stat-icon {{
            font-size: 1.5rem;
            margin-bottom: 0.75rem;
            opacity: 0.8;
        }}

        .stat-number {{
            font-family: var(--font-display);
            font-size: clamp(2rem, 5vw, 3rem);
            font-weight: 700;
            color: var(--accent);
            line-height: 1;
        }}

        .stat-unit {{
            font-size: 0.5em;
            opacity: 0.7;
        }}

        .stat-label {{
            font-size: var(--small-size);
            color: var(--text-secondary);
            margin-top: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        /* ==========================================
           任务列表
           ========================================== */
        .tasks-list {{
            display: flex;
            flex-direction: column;
            gap: var(--element-gap);
        }}

        .task-card {{
            background: {"rgba(255,255,255,0.03)" if not is_light else "rgba(0,0,0,0.03)"};
            border: 1px solid {"rgba(255,255,255,0.08)" if not is_light else "rgba(0,0,0,0.08)"};
            border-radius: 12px;
            padding: clamp(1rem, 2vw, 1.25rem);
            transition: transform 0.3s var(--ease-out-expo), border-color 0.3s;
        }}

        .task-card:hover {{
            transform: translateX(8px);
            border-color: var(--accent);
        }}

        .task-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}

        .task-category {{
            font-size: var(--small-size);
            font-weight: 500;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            background: var(--accent);
            color: {"#000" if not is_light else "#fff"};
        }}

        .task-hours {{
            font-size: var(--small-size);
            color: var(--text-secondary);
            font-family: var(--font-display);
        }}

        .task-title {{
            font-size: var(--body-size);
            font-weight: 500;
            line-height: 1.4;
        }}

        .task-progress-bar {{
            height: 6px;
            background: {"rgba(255,255,255,0.1)" if not is_light else "rgba(0,0,0,0.1)"};
            border-radius: 3px;
            margin-top: 0.75rem;
            position: relative;
            overflow: hidden;
        }}

        .task-progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--accent-secondary));
            border-radius: 3px;
            transition: width 1s var(--ease-out-expo);
        }}

        .task-progress-text {{
            position: absolute;
            right: 0;
            top: -1.25rem;
            font-size: 0.75rem;
            color: var(--text-secondary);
        }}

        /* ==========================================
           分类统计
           ========================================== */
        .category-chart {{
            display: flex;
            flex-direction: column;
            gap: var(--element-gap);
        }}

        .category-item {{
            background: {"rgba(255,255,255,0.03)" if not is_light else "rgba(0,0,0,0.03)"};
            border-radius: 10px;
            overflow: hidden;
        }}

        .category-bar-container {{
            height: 4px;
            background: {"rgba(255,255,255,0.05)" if not is_light else "rgba(0,0,0,0.05)"};
        }}

        .category-bar {{
            height: 100%;
            transition: width 1s var(--ease-out-expo);
        }}

        .category-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.25rem;
        }}

        .category-name {{
            font-weight: 500;
        }}

        .category-stats {{
            font-size: var(--small-size);
            color: var(--text-secondary);
        }}

        .category-summary {{
            text-align: center;
            margin-top: var(--content-gap);
            color: var(--text-secondary);
            font-size: var(--body-size);
        }}

        .category-summary strong {{
            color: var(--accent);
        }}

        /* ==========================================
           计划列表
           ========================================== */
        .plans-list {{
            display: flex;
            flex-direction: column;
            gap: var(--element-gap);
        }}

        .plan-item {{
            display: flex;
            align-items: flex-start;
            gap: 1.25rem;
            background: {"rgba(255,255,255,0.03)" if not is_light else "rgba(0,0,0,0.03)"};
            border-radius: 12px;
            padding: clamp(1rem, 2vw, 1.5rem);
            transition: transform 0.3s var(--ease-out-expo);
        }}

        .plan-item:hover {{
            transform: translateX(8px);
        }}

        .plan-number {{
            font-family: var(--font-display);
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent);
            opacity: 0.5;
            line-height: 1;
        }}

        .plan-title {{
            font-weight: 500;
            margin-bottom: 0.25rem;
        }}

        .plan-meta {{
            font-size: var(--small-size);
            color: var(--text-secondary);
        }}

        /* ==========================================
           结束页
           ========================================== */
        .end-slide {{
            text-align: center;
        }}

        .end-slide h2::after {{
            left: 50%;
            transform: translateX(-50%);
        }}

        .end-icon {{
            font-size: 4rem;
            margin-bottom: 1.5rem;
        }}

        .end-summary {{
            font-size: clamp(1.125rem, 2.5vw, 1.5rem);
            color: var(--text-secondary);
            margin: 1.5rem 0;
            line-height: 1.8;
        }}

        .end-summary strong {{
            color: var(--accent);
            font-weight: 600;
        }}

        .end-message {{
            font-size: clamp(1.5rem, 4vw, 2.5rem);
            font-weight: 600;
            margin-top: 1rem;
        }}

        /* ==========================================
           进场动画
           ========================================== */
        .reveal {{
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.8s var(--ease-out-expo),
                        transform 0.8s var(--ease-out-expo);
        }}

        .slide.visible .reveal {{
            opacity: 1;
            transform: translateY(0);
        }}

        /* ==========================================
           进度条 & 导航
           ========================================== */
        .progress-bar {{
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent), var(--accent-secondary));
            z-index: 1000;
            transition: width 0.3s ease;
        }}

        .nav-dots {{
            position: fixed;
            right: clamp(1rem, 2vw, 2rem);
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            z-index: 1000;
        }}

        .nav-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--text-secondary);
            opacity: 0.3;
            cursor: pointer;
            transition: all 0.3s var(--ease-out-expo);
        }}

        .nav-dot.active {{
            opacity: 1;
            background: var(--accent);
            transform: scale(1.3);
        }}

        .nav-dot:hover {{
            opacity: 0.7;
        }}

        /* ==========================================
           响应式断点
           ========================================== */
        @media (max-height: 700px) {{
            :root {{
                --slide-padding: clamp(1rem, 4vw, 2.5rem);
                --content-gap: clamp(0.75rem, 2vw, 1.5rem);
            }}
        }}

        @media (max-height: 500px) {{
            .nav-dots, .scroll-hint {{
                display: none;
            }}
        }}

        @media (max-width: 600px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .nav-dots {{
                display: none;
            }}
        }}

        /* ==========================================
           减少动画偏好
           ========================================== */
        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{
                animation-duration: 0.01ms !important;
                transition-duration: 0.3s !important;
            }}

            html {{
                scroll-behavior: auto;
            }}
        }}

        /* ==========================================
           打印样式
           ========================================== */
        @media print {{
            .slide {{
                page-break-after: always;
                height: auto;
                min-height: 100vh;
            }}

            .nav-dots, .progress-bar, .scroll-hint, .slide-bg-effect {{
                display: none !important;
            }}

            .reveal {{
                opacity: 1 !important;
                transform: none !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="progress-bar" id="progressBar"></div>
    <nav class="nav-dots" id="navDots"></nav>

    {slides_html}

    <script>
        class SlidePresentation {{
            constructor() {{
                this.slides = document.querySelectorAll('.slide');
                this.currentSlide = 0;
                this.progressBar = document.getElementById('progressBar');
                this.navDots = document.getElementById('navDots');
                this.isScrolling = false;

                this.init();
            }}

            init() {{
                this.setupIntersectionObserver();
                this.setupKeyboardNav();
                this.setupNavDots();
                this.updateProgress();

                // 初始显示第一张
                setTimeout(() => {{
                    this.slides[0].classList.add('visible');
                }}, 100);
            }}

            setupIntersectionObserver() {{
                const options = {{
                    root: null,
                    rootMargin: '0px',
                    threshold: 0.6
                }};

                const observer = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            entry.target.classList.add('visible');
                            const index = Array.from(this.slides).indexOf(entry.target);
                            this.currentSlide = index;
                            this.updateProgress();
                            this.updateNavDots();
                        }}
                    }});
                }}, options);

                this.slides.forEach(slide => observer.observe(slide));
            }}

            setupKeyboardNav() {{
                document.addEventListener('keydown', (e) => {{
                    if (this.isScrolling) return;

                    if (['ArrowDown', ' ', 'PageDown', 'Enter'].includes(e.key)) {{
                        e.preventDefault();
                        this.nextSlide();
                    }} else if (['ArrowUp', 'PageUp'].includes(e.key)) {{
                        e.preventDefault();
                        this.prevSlide();
                    }} else if (e.key === 'Home') {{
                        e.preventDefault();
                        this.goToSlide(0);
                    }} else if (e.key === 'End') {{
                        e.preventDefault();
                        this.goToSlide(this.slides.length - 1);
                    }}
                }});
            }}

            setupNavDots() {{
                this.slides.forEach((_, index) => {{
                    const dot = document.createElement('div');
                    dot.className = 'nav-dot' + (index === 0 ? ' active' : '');
                    dot.addEventListener('click', () => this.goToSlide(index));
                    this.navDots.appendChild(dot);
                }});
            }}

            updateNavDots() {{
                const dots = this.navDots.querySelectorAll('.nav-dot');
                dots.forEach((dot, index) => {{
                    dot.classList.toggle('active', index === this.currentSlide);
                }});
            }}

            updateProgress() {{
                const progress = ((this.currentSlide + 1) / this.slides.length) * 100;
                this.progressBar.style.width = progress + '%';
            }}

            goToSlide(index) {{
                if (index >= 0 && index < this.slides.length && !this.isScrolling) {{
                    this.isScrolling = true;
                    this.slides[index].scrollIntoView({{ behavior: 'smooth' }});
                    setTimeout(() => {{ this.isScrolling = false; }}, 800);
                }}
            }}

            nextSlide() {{
                if (this.currentSlide < this.slides.length - 1) {{
                    this.goToSlide(this.currentSlide + 1);
                }}
            }}

            prevSlide() {{
                if (this.currentSlide > 0) {{
                    this.goToSlide(this.currentSlide - 1);
                }}
            }}
        }}

        // 初始化
        document.addEventListener('DOMContentLoaded', () => {{
            new SlidePresentation();
        }});
    </script>
</body>
</html>'''


def get_available_styles() -> Dict[str, str]:
    """获取可用的演示风格列表"""
    return {key: f"{value['name_cn']} ({value['name']})" for key, value in PRESENTATION_STYLES.items()}
