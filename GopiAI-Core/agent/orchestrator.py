"""
Модуль оркестратора агентов.

Предоставляет реализацию оркестратора, который управляет специализированными агентами
и координирует их работу.
"""

from typing import Dict, Any, Optional

from gopiai.app.agent.agent_manager import AgentManager
from gopiai.app.agent.hybrid_browser_agent import HybridBrowserAgent
from gopiai.app.agent.specialized_agent import SpecializedAgent
from gopiai.core.logging import get_logger
logger = get_logger().logger

# Глобальный экземпляр оркестратора
_orchestrator = None

class AgentOrchestrator:
    """
    Оркестратор агентов.
    
    Управляет специализированными агентами и координирует их работу.
    """
    
    def __init__(self):
        """Инициализирует оркестратора."""
        self.specialized_agents: Dict[str, SpecializedAgent] = {}
        self.agent_manager = AgentManager.instance()
        self.project_index = {}
        
    async def create_specialized_agent(self, agent_id: str, task_description: str, context: Optional[Dict[str, Any]] = None) -> SpecializedAgent:
        """
        Создает специализированного агента.
        
        Args:
            agent_id: Идентификатор агента
            task_description: Описание задачи
            context: Контекст для агента
            
        Returns:
            SpecializedAgent: Созданный агент
        """
        # Создаем агента
        agent = SpecializedAgent()
        
        # Устанавливаем контекст
        context = context or {}
        context["task"] = task_description
        await agent.set_context(context)
        
        # Сохраняем агента
        self.specialized_agents[agent_id] = agent
        
        logger.info(f"Создан специализированный агент: {agent_id}")
        
        return agent
        
    async def create_hybrid_browser_agent(self, agent_id: str, task_description: str, preferred_tool: str = "auto", browser = None, context: Optional[Dict[str, Any]] = None) -> HybridBrowserAgent:
        """
        Создает гибридного браузерного агента.
        
        Args:
            agent_id: Идентификатор агента
            task_description: Описание задачи
            preferred_tool: Предпочтительный инструмент
            browser: Экземпляр браузера
            context: Контекст для агента
            
        Returns:
            HybridBrowserAgent: Созданный агент
        """
        # Создаем агента
        agent = HybridBrowserAgent(
            preferred_tool=preferred_tool,
            browser=browser
        )
        
        # Устанавливаем контекст
        context = context or {}
        context["task"] = task_description
        await agent.set_context(context)
        
        # Сохраняем агента
        self.specialized_agents[agent_id] = agent
        
        logger.info(f"Создан гибридный браузерный агент: {agent_id}")
        
        return agent
        
    async def get_agent(self, agent_id: str) -> Optional[SpecializedAgent]:
        """
        Возвращает агента по идентификатору.
        
        Args:
            agent_id: Идентификатор агента
            
        Returns:
            SpecializedAgent: Агент или None, если агент не найден
        """
        return self.specialized_agents.get(agent_id)
        
    async def provide_guidance(self, agent_id: str, guidance: str) -> bool:
        """
        Предоставляет руководство агенту.
        
        Args:
            agent_id: Идентификатор агента
            guidance: Руководство
            
        Returns:
            bool: True, если руководство успешно предоставлено
        """
        agent = self.specialized_agents.get(agent_id)
        if not agent:
            logger.warning(f"Агент не найден: {agent_id}")
            return False
            
        await agent.receive_guidance(guidance)
        return True
        
    async def process_query(self, agent_id: str, query: str) -> str:
        """
        Обрабатывает запрос с помощью агента.
        
        Args:
            agent_id: Идентификатор агента
            query: Запрос
            
        Returns:
            str: Результат обработки запроса
        """
        agent = self.specialized_agents.get(agent_id)
        if not agent:
            logger.warning(f"Агент не найден: {agent_id}")
            return f"Агент не найден: {agent_id}"
            
        return await agent.process(query)
        
    async def index_project(self, project_path: str) -> Dict[str, Any]:
        """
        Индексирует проект.
        
        Args:
            project_path: Путь к проекту
            
        Returns:
            Dict[str, Any]: Индекс проекта
        """
        # В минимальной версии просто возвращаем заглушку
        self.project_index = {
            "files": {
                "file1.py": {
                    "summary": "Пример файла 1",
                    "imports": ["os", "sys"],
                    "functions": ["func1", "func2"]
                },
                "file2.py": {
                    "summary": "Пример файла 2",
                    "imports": ["json", "datetime"],
                    "functions": ["func3", "func4"]
                }
            },
            "dependencies": {
                "python": ["os", "sys", "json", "datetime"]
            },
            "architecture": {
                "patterns": ["MVC", "Factory"]
            }
        }
        
        return self.project_index
        
    async def extract_context(self, query: str, agent_type: str = "specialized") -> Dict[str, Any]:
        """
        Извлекает контекст для агента на основе запроса.
        
        Args:
            query: Запрос
            agent_type: Тип агента
            
        Returns:
            Dict[str, Any]: Контекст для агента
        """
        # В минимальной версии просто возвращаем заглушку
        context = {
            "task": query,
            "relevant_files": {
                "file1.py": {
                    "summary": "Пример файла 1"
                }
            },
            "dependencies": {
                "python": ["os", "sys"]
            },
            "architecture": {
                "patterns": ["MVC"]
            }
        }
        
        return context
        
    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Возвращает текущее состояние агента.
        
        Args:
            agent_id: Идентификатор агента
            
        Returns:
            Dict[str, Any]: Текущее состояние агента или None, если агент не найден
        """
        agent = self.specialized_agents.get(agent_id)
        if not agent:
            return None
            
        return agent.get_current_state()
        
    async def cleanup(self):
        """Очищает ресурсы оркестратора."""
        for agent_id, agent in self.specialized_agents.items():
            if hasattr(agent, "cleanup") and callable(agent.cleanup):
                await agent.cleanup()
                
        self.specialized_agents.clear()
        logger.info("Ресурсы оркестратора очищены")


def get_orchestrator() -> AgentOrchestrator:
    """
    Возвращает глобальный экземпляр оркестратора.
    
    Returns:
        AgentOrchestrator: Глобальный экземпляр оркестратора
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
