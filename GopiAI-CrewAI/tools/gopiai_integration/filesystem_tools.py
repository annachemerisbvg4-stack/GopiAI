from crewai.tools.base_tool import BaseTool
from pydantic import Field

class GopiAIFileSystemTool(BaseTool):
    name: str = Field(default="gopiai_filesystem", description="Имя инструмента")
    description: str = Field(default="Инструмент для работы с файловой системой", description="Описание инструмента")

    def _run(self, action: str, path: str = "", data: str = "", **kwargs):
        if action == "read":
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        elif action == "write":
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
            return "OK"
        else:
            raise ValueError(f"Неизвестное действие: {action}")
