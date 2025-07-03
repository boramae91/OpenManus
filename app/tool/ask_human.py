import os

from app.tool import BaseTool


class AskHuman(BaseTool):
    """Add a tool to ask human for help."""

    name: str = "ask_human"
    description: str = "Use this tool to ask human for help."
    parameters: str = {
        "type": "object",
        "properties": {
            "inquire": {
                "type": "string",
                "description": "The question you want to ask human.",
            }
        },
        "required": ["inquire"],
    }

    async def execute(self, inquire: str) -> str:
        # 대시보드 모드에서는 ask_human 도구를 비활성화
        dashboard_mode = os.getenv("DASHBOARD_MODE", "false").lower() == "true"
        streamlit_mode = os.getenv("STREAMLIT_MODE", "false").lower() == "true"

        if dashboard_mode or streamlit_mode:
            return "대시보드 모드에서는 사용자 입력이 비활성화되어 있습니다. 자동으로 '건너뛰기'로 처리합니다."

        return input(f"""Bot: {inquire}\n\nYou: """).strip()
