"""
Инструмент для редактирования файлов с помощью замены строк.
"""

from pathlib import Path

from gopiai.app.config import WORKSPACE_ROOT
from gopiai.app.interfaces import ToolResult
from gopiai.app.tool.base import BaseTool


class StrReplaceEditor(BaseTool):
    """Инструмент для редактирования файлов с помощью замены строк."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="str_replace_editor",
            description="Редактирует файлы с помощью замены строк",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Путь к файлу"
                    },
                    "old_str": {
                        "type": "string",
                        "description": "Строка для замены"
                    },
                    "new_str": {
                        "type": "string",
                        "description": "Новая строка"
                    },
                    "create_if_not_exists": {
                        "type": "boolean",
                        "description": "Создать файл, если он не существует"
                    }
                },
                "required": ["file_path", "old_str", "new_str"]
            }
        )
    
    async def execute(self, **kwargs):
        """Выполняет инструмент с указанными параметрами."""
        return await self._edit(**kwargs)
    
    async def _edit(self, file_path, old_str, new_str, create_if_not_exists=False):
        """
        Редактирует файл с помощью замены строк.
        
        Args:
            file_path: Путь к файлу
            old_str: Строка для замены
            new_str: Новая строка
            create_if_not_exists: Создать файл, если он не существует
            
        Returns:
            dict: Результат операции
        """
        try:
            # Проверяем, что путь к файлу находится в рабочей директории
            abs_path = Path(file_path)
            if not abs_path.is_absolute():
                abs_path = WORKSPACE_ROOT / file_path
                
            # Проверяем, что файл существует
            if not abs_path.exists():
                if create_if_not_exists:
                    # Создаем директории, если они не существуют
                    abs_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Создаем файл
                    with open(abs_path, "w", encoding="utf-8") as f:
                        f.write("")
                else:
                    return ToolResult(
                        message=f"Файл не существует: {file_path}",
                        data={"error": f"File not found: {file_path}"},
                        success=False
                    )
                    
            # Читаем содержимое файла
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Заменяем строку
            new_content = content.replace(old_str, new_str)
            
            # Если содержимое не изменилось, возвращаем сообщение
            if new_content == content:
                return ToolResult(
                    message=f"Строка '{old_str}' не найдена в файле {file_path}",
                    data={"error": f"Text not found in file: {old_str}"},
                    success=False
                )
                
            # Записываем новое содержимое
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            return ToolResult(
                message=f"Строка '{old_str}' заменена на '{new_str}' в файле {file_path}",
                data={"replacements": 1, "file_path": str(file_path)}
            )
        except Exception as e:
            return ToolResult(
                message=f"Ошибка при редактировании файла: {str(e)}",
                data={"error": str(e)},
                success=False
            )
