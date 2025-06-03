import json
from typing import Any, Dict, Optional

from pydantic import Field

from gopiai.app.agent.toolcall import ToolCallAgent
from gopiai.core.logging import get_logger
logger = get_logger().logger
from gopiai.app.prompt.coding import CODING_AGENT_NEXT_STEP_PROMPT, CODING_AGENT_SYSTEM_PROMPT
from gopiai.app.schema import ToolChoice
from gopiai.app.tool.code_tools_integration import get_coding_tools
from gopiai.app.tool.terminate import Terminate
from gopiai.app.tool.tool_collection import ToolCollection


class CodingAgent(ToolCallAgent):
    """
    Агент для работы с кодом и IDE.

    Этот агент может открывать, редактировать, анализировать и запускать код,
    используя встроенный редактор и инструменты для работы с кодом.
    """

    name: str = "coding_agent"
    description: str = (
        "Агент для работы с кодом, который может редактировать, анализировать и запускать код"
    )

    # Подсказки для системы и следующего шага
    system_prompt: str = CODING_AGENT_SYSTEM_PROMPT
    next_step_prompt: str = CODING_AGENT_NEXT_STEP_PROMPT

    # Ограничения
    max_observe: int = 15000
    max_steps: int = 30

    # Используем правильное имя поля tools вместо coding_tools
    tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(Terminate())
    )

    # Выбор инструментов (AUTO позволяет как использовать инструменты, так и давать ответы)
    tool_choices: ToolChoice = ToolChoice.AUTO

    # Специальные инструменты
    special_tool_names: list[str] = Field(
        default_factory=lambda: [Terminate().terminate_name]
    )

    # Сохраненное состояние редактора кода
    _current_editor_state: Optional[Dict] = None

    def __init__(self, **data):
        super().__init__(**data)

        # Добавляем инструменты для работы с кодом
        code_tools = get_coding_tools()
        for tool in code_tools:
            self.tools.add_tool(tool)

        logger.info(
            f"Инициализирован {self.name} с {len(self.tools.tools)} инструментами"
        )

    async def _handle_special_tool(self, name: str, result: Any, **kwargs):
        """Обработка вызова специальных инструментов."""
        if not self._is_special_tool(name):
            return
        else:
            await super()._handle_special_tool(name, result, **kwargs)

    async def get_editor_state(self) -> Optional[Dict]:
        """
        Получает текущее состояние редактора кода для контекста следующих шагов.

        Returns:
            Dict с состоянием редактора или None, если информация недоступна
        """
        return self._current_editor_state

    async def update_editor_state(self):
        """
        Обновляет сохраненное состояние редактора кода.

        Получает информацию об открытых файлах, текущем файле и позиции курсора.
        """
        try:
            # Пытаемся получить информацию об открытых файлах
            code_control = self.tools.get_tool("code_control")
            if code_control:
                # Получаем список открытых файлов
                files_result = await code_control.execute(action="get_open_files")

                if not files_result.error:
                    files_info = files_result.output
                else:
                    files_info = "Не удалось получить информацию об открытых файлах"

                # Получаем текущий файл
                current_file_result = await code_control.execute(
                    action="get_current_file"
                )
                if not current_file_result.error:
                    current_file = current_file_result.output
                else:
                    current_file = "Не удалось получить текущий файл"

                # Сохраняем состояние
                self._current_editor_state = {
                    "open_files": files_info,
                    "current_file": current_file,
                }

                return self._current_editor_state
        except Exception as e:
            logger.error(f"Ошибка при обновлении состояния редактора: {e}")

        return None

    async def think(self) -> bool:
        """
        Обрабатывает текущее состояние и решает, какие действия выполнять дальше,
        используя инструменты с добавлением информации о состоянии редактора кода.

        Returns:
            bool: True, если обработка успешна, False в противном случае
        """
        # Сначала обновляем информацию о редакторе
        await self.update_editor_state()

        # Вызываем родительский метод для обработки текущего состояния
        result = await super().think()
        return result

    async def format_next_step_prompt(self) -> str:
        """
        Форматирует подсказку для следующего шага с учетом состояния редактора.

        Returns:
            str: Отформатированная подсказка для следующего шага
        """
        editor_state = await self.get_editor_state()
        editor_state_str = ""

        if editor_state:
            editor_state_str = f"Текущее состояние редактора: {json.dumps(editor_state, ensure_ascii=False)}"

        # Заменяем метку {editor_state} в подсказке для следующего шага
        next_prompt = self.next_step_prompt.replace("{editor_state}", editor_state_str)

        return next_prompt
