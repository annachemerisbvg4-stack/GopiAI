import unittest

class TestAgent(unittest.TestCase):

    def test_agent_import_error(self):
        with self.assertRaises(ImportError):
            from your_module import Agent  # Replace your_module
            Agent()

    def test_agent_init_raises_import_error(self):
        from your_module import Agent  # Replace your_module
        with self.assertRaises(ImportError) as context:
            Agent()
        self.assertEqual(str(context.exception), 'smolagents is not available - install "agent" extra to enable')

    def test_agent_init_raises_import_error_with_args(self):
        from your_module import Agent  # Replace your_module
        with self.assertRaises(ImportError) as context:
            Agent(1, 2, 3)
        self.assertEqual(str(context.exception), 'smolagents is not available - install "agent" extra to enable')

    def test_agent_init_raises_import_error_with_kwargs(self):
        from your_module import Agent  # Replace your_module
        with self.assertRaises(ImportError) as context:
            Agent(a=1, b=2)
        self.assertEqual(str(context.exception), 'smolagents is not available - install "agent" extra to enable')

    def test_agent_init_raises_import_error_with_args_and_kwargs(self):
        from your_module import Agent  # Replace your_module
        with self.assertRaises(ImportError) as context:
            Agent(1, 2, a=1, b=2)
        self.assertEqual(str(context.exception), 'smolagents is not available - install "agent" extra to enable')