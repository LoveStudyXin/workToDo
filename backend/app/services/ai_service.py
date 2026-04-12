import httpx
from typing import Optional
from app.core.config import settings


class AIService:
    """AI service supporting multiple Chinese LLM providers"""

    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.timeout = 60.0

    async def enhance_report(self, raw_content: str, report_type: str) -> Optional[str]:
        """Enhance report content using AI"""

        prompt = self._build_prompt(raw_content, report_type)

        try:
            if self.provider == "deepseek":
                return await self._call_deepseek(prompt)
            elif self.provider == "qwen":
                return await self._call_qwen(prompt)
            elif self.provider == "wenxin":
                return await self._call_wenxin(prompt)
            else:
                return None
        except Exception as e:
            print(f"AI enhancement failed: {e}")
            return None

    async def generate_template(self, user_input: str, template_type: str, mode: str) -> Optional[str]:
        """Generate template using AI

        Args:
            user_input: User's description or existing report content
            template_type: daily/weekly/monthly/yearly
            mode: 'describe' (from description) or 'convert' (from existing content)
        """
        prompt = self._build_template_prompt(user_input, template_type, mode)

        try:
            if self.provider == "deepseek":
                return await self._call_deepseek(prompt)
            elif self.provider == "qwen":
                return await self._call_qwen(prompt)
            elif self.provider == "wenxin":
                return await self._call_wenxin(prompt)
            else:
                return None
        except Exception as e:
            print(f"AI template generation failed: {e}")
            return None

    def _build_template_prompt(self, user_input: str, template_type: str, mode: str) -> str:
        type_names = {
            "daily": "日报",
            "weekly": "周报",
            "monthly": "月报",
            "yearly": "年度绩效报告"
        }
        type_name = type_names.get(template_type, "工作报告")

        available_vars = """
可用的变量占位符（按需使用，不必全部使用）：
- {{date_range}} - 日期范围
- {{completed_tasks}} - 已完成任务列表
- {{in_progress_tasks}} - 进行中任务列表
- {{total_hours}} - 工作时长统计
- {{completed_count}} - 完成任务数
- {{category_stats}} - 分类统计
- {{highlights}} - 亮点/成果
- {{issues}} - 问题/困难
- {{next_plans}} - 下一步计划
"""

        if mode == "describe":
            return f"""你是一个工作报告模板设计师。请根据用户的需求，生成一个简洁的{type_name}模板。

用户需求：
{user_input}

{available_vars}

重要要求：
1. 只包含用户明确提到的内容，不要擅自添加额外章节
2. 保持简洁，不要过度设计
3. 使用 Markdown 格式
4. 只在必要时使用变量占位符

请直接输出模板内容："""
        else:  # convert mode
            return f"""你是一个工作报告模板设计师。请将用户的报告内容转换为模板。

用户的报告内容：
{user_input}

{available_vars}

重要要求：
1. 严格保留原报告的结构，不要添加原文没有的章节
2. 只将具体内容替换为变量占位符，保持原有格式
3. 使用 Markdown 格式
4. 不要扩展或美化，保持原样式

请直接输出模板内容："""

    def _build_prompt(self, raw_content: str, report_type: str) -> str:
        type_names = {
            "daily": "日报",
            "weekly": "周报",
            "monthly": "月报",
            "yearly": "年度绩效报告"
        }
        type_name = type_names.get(report_type, "工作报告")

        return f"""请帮我润色以下{type_name}中的具体内容。

严格要求：
1. 完全保留原有的标题、章节结构，不要修改任何标题
2. 不要添加新的章节或删除现有章节
3. 只润色每个章节下的具体内容（任务列表、描述文字等）
4. 让任务描述更专业、简洁
5. 保持列表格式（如 "- " 开头的列表项）
6. 不要添加总结性段落或过渡语句

原始内容：
{raw_content}

请直接输出润色后的报告，保持完全相同的结构："""

    async def _call_deepseek(self, prompt: str) -> Optional[str]:
        """Call DeepSeek API"""
        api_key = settings.DEEPSEEK_API_KEY or settings.AI_API_KEY
        if not api_key:
            return None

        base_url = settings.DEEPSEEK_BASE_URL or settings.AI_BASE_URL

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4096
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_qwen(self, prompt: str) -> Optional[str]:
        """Call Qwen (通义千问) API"""
        api_key = settings.QWEN_API_KEY or settings.AI_API_KEY
        if not api_key:
            return None

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{settings.QWEN_BASE_URL}/services/aigc/text-generation/generation",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "qwen-turbo",
                    "input": {
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    },
                    "parameters": {
                        "temperature": 0.7,
                        "max_tokens": 4096
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["output"]["text"]

    async def _call_wenxin(self, prompt: str) -> Optional[str]:
        """Call Wenxin (文心一言) API"""
        api_key = settings.WENXIN_API_KEY
        secret_key = settings.WENXIN_SECRET_KEY
        if not api_key or not secret_key:
            return None

        # First get access token
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            token_response = await client.post(
                f"https://aip.baidubce.com/oauth/2.0/token",
                params={
                    "grant_type": "client_credentials",
                    "client_id": api_key,
                    "client_secret": secret_key
                }
            )
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                return None

            # Call chat API
            response = await client.post(
                f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
                params={"access_token": access_token},
                headers={"Content-Type": "application/json"},
                json={
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("result")


ai_service = AIService()
