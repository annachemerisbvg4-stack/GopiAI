import unittest
import os
import shutil
from crewai.tools.base_tool import BaseTool
from pydantic import Field

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

class TestGopiAIFileSystemTool(unittest.TestCase):

    def setUp(self):
        self.tool = GopiAIFileSystemTool()
        self.test_dir = "test_dir"
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_write_and_read(self):
        message = "Hello, world!"
        self.tool._run("write", path=self.test_file, data=message)
        content = self.tool._run("read", path=self.test_file)
        self.assertEqual(content, message)

    def test_append(self):
        initial_message = "Hello, "
        append_message = "world!"
        self.tool._run("write", path=self.test_file, data=initial_message)
        self.tool._run("append", path=self.test_file, data=append_message)
        content = self.tool._run("read", path=self.test_file)
        self.assertEqual(content, initial_message + append_message)

    def test_delete(self):
        self.tool._run("write", path=self.test_file, data="test")
        self.assertTrue(os.path.exists(self.test_file))
        self.tool._run("delete", path=self.test_file)
        self.assertFalse(os.path.exists(self.test_file))

    def test_list_directory(self):
        self.tool._run("write", path=os.path.join(self.test_dir, "file1.txt"), data="test")
        self.tool._run("write", path=os.path.join(self.test_dir, "file2.txt"), data="test")
        files = self.tool._run("list", path=self.test_dir)
        self.assertIn("file1.txt", files)
        self.assertIn("file2.txt", files)

    def test_mkdir_and_remove_directory(self):
        new_dir = os.path.join(self.test_dir, "new_dir")
        self.tool._run("mkdir", path=new_dir)
        self.assertTrue(os.path.exists(new_dir))
        self.tool._run("remove", path=new_dir)
        self.assertFalse(os.path.exists(new_dir))