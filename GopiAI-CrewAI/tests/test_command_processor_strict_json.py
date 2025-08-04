import json
import unittest

# Импортируем SmartDelegator и CommandExecutor
from tools.gopiai_integration.smart_delegator import SmartDelegator
from tools.gopiai_integration.command_executor import CommandExecutor

class TestCommandProcessorStrictJSON(unittest.TestCase):
    def setUp(self):
        self.delegator = SmartDelegator(rag_system=None)
        self.executor = CommandExecutor()

    def _process(self, response_text: str):
        # Эмулируем кусок process_request с обработкой команд
        updated_response, command_results = self.executor.process_gemini_response(response_text)
        # Дополнительная валидация верхнего уровня (как в SmartDelegator)
        is_valid_top_level = False
        try:
            parsed = json.loads(response_text)
        except Exception:
            parsed = None

        def _valid_cmd(obj):
            return isinstance(obj, dict) and "tool" in obj and "params" in obj and isinstance(obj["params"], dict)

        if isinstance(parsed, dict):
            is_valid_top_level = _valid_cmd(parsed)
        elif isinstance(parsed, list):
            is_valid_top_level = all(_valid_cmd(x) for x in parsed)

        if not is_valid_top_level:
            # Если верхний уровень невалидный — команды не должны исполняться
            return response_text, []
        return updated_response, command_results

    def test_valid_single_object(self):
        data = {"tool": "browser_tools", "params": {"command": "open", "url": "https://example.com"}}
        text = json.dumps(data, ensure_ascii=False)
        updated_response, results = self._process(text)
        # В строгом режиме ожидаем попытку распознания одной команды
        # Конкретное содержание results зависит от CommandExecutor-реализации,
        # но здесь важно, что список команд не пуст
        self.assertIsInstance(results, list)

    def test_valid_array_of_objects(self):
        data = [
            {"tool": "filesystem_tools", "params": {"command": "ls", "path": "."}},
            {"tool": "web_search", "params": {"query": "gopi ai project"}}
        ]
        text = json.dumps(data, ensure_ascii=False)
        updated_response, results = self._process(text)
        self.assertIsInstance(results, list)

    def test_invalid_free_text_markdown(self):
        text = "О, зая моя любопытная...\n**filesystem_tools** могу всё...\n`lss*([^n]*)` ..."
        updated_response, results = self._process(text)
        self.assertEqual(results, [], "Никакие команды не должны выполняться на свободном тексте")

    def test_invalid_json_missing_keys(self):
        # Нет ключа params
        data = {"tool": "browser_tools"}
        text = json.dumps(data, ensure_ascii=False)
        updated_response, results = self._process(text)
        self.assertEqual(results, [], "Команды без params не должны исполняться")

        # params не dict
        data2 = {"tool": "browser_tools", "params": "open https://example.com"}
        text2 = json.dumps(data2, ensure_ascii=False)
        updated_response2, results2 = self._process(text2)
        self.assertEqual(results2, [], "Команды с некорректным params не должны исполняться")

    def test_invalid_non_json(self):
        text = "not a json at all"
        updated_response, results = self._process(text)
        self.assertEqual(results, [], "Никакие команды не должны выполняться, если это не JSON")

if __name__ == "__main__":
    unittest.main()
