# Импортируем BaseTool из crewai
from crewai.tools.base_tool import BaseTool
from pydantic import Field
import os
import shutil

class GopiAIFileSystemTool(BaseTool):
    name: str = Field(default="gopiai_filesystem", description="Имя инструмента")
    description: str = Field(default="Инструмент для работы с файловой системой", description="Описание инструмента")

    def _run(self, action: str, path: str = "", data: str = "", **kwargs):
        try:
            if action == "read":
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            elif action == "write":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(data)
                return f"Файл '{path}' успешно записан."
            elif action == "append":
                with open(path, "a", encoding="utf-8") as f:
                    f.write(data)
                return f"Данные добавлены в файл '{path}'."
            elif action == "delete":
                os.remove(path)
                return f"Файл '{path}' удалён."
            elif action == "list":
                if os.path.isdir(path):
                    return os.listdir(path)
                else:
                    return f"Путь '{path}' не является директорией."
            elif action == "exists":
                return os.path.exists(path)
            elif action == "mkdir":
                os.makedirs(path, exist_ok=True)
                return f"Директория '{path}' создана."
            elif action == "remove":
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    return f"Директория '{path}' удалена."
                else:
                    os.remove(path)
                    return f"Файл '{path}' удалён."
            elif action == "copy":
                dst = kwargs.get("dst")
                if not dst:
                    return "Не указан путь назначения (dst)."
                shutil.copy2(path, dst)
                return f"Файл скопирован из '{path}' в '{dst}'."
            elif action == "move":
                dst = kwargs.get("dst")
                if not dst:
                    return "Не указан путь назначения (dst)."
                shutil.move(path, dst)
                return f"Файл перемещён из '{path}' в '{dst}'."
            else:
                raise ValueError(f"Неизвестное действие: {action}")
        except Exception as e:
            return f"Ошибка файловой операции: {e}"
