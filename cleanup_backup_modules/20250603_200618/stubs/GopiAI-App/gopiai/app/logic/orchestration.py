#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 📅 TODO_STUB_SEARCH: найти командой grep -r 'TODO_STUB' .

"""
Модуль для интеграции оркестратора с контроллером агентов.

Предоставляет функциональность для создания и управления
специализированными агентами через контроллер агентов.
"""

import asyncio

from PySide6.QtCore import QObject, Signal, Slot
from gopiai.app.agent.agent_manager import AgentManager
from gopiai.app.agent.orchestrator import get_orchestrator
from gopiai.core.logging import get_logger
logger = get_logger().logger
from gopiai.app.logic.agent_controller import AgentController
from gopiai.app.tool.serena_memory_tool import get_orchestration_tools


class OrchestrationController(QObject):
    """
    Контроллер для интеграции оркестратора с контроллером агентов.
    
    Предоставляет методы для создания и управления специализированными агентами
    через контроллер агентов.
    """
    
    # Сигналы
    agent_created = Signal(str)  # agent_id
    agent_monitored = Signal(str, bool)  # agent_id, has_guidance
    project_indexed = Signal(bool)  # success
    
    def __init__(self, agent_controller=None):
        """
        Инициализирует контроллер оркестрации.
        
        Args:
            agent_controller: Экземпляр контроллера агентов
        """
        super().__init__()
        self.agent_controller = agent_controller or AgentController.instance()
        self.orchestrator = get_orchestrator()
        self.specialized_components = {}  # component_id -> agent_id
        
        # Добавляем инструменты оркестрации в контроллер агентов
        self._add_orchestration_tools()
    
    def _add_orchestration_tools(self):
        """Добавляет инструменты оркестрации в контроллер агентов."""
        try:
            # Получаем инструменты оркестрации
            orchestration_tools = get_orchestration_tools()
            
            # Добавляем инструменты в контроллер агентов
            for tool in orchestration_tools:
                self.agent_controller.add_tool(tool)
                
            logger.info("Orchestration tools added to agent controller")
        except Exception as e:
            logger.error(f"Error adding orchestration tools: {str(e)}")
    
    @Slot(str)
    def index_project(self, project_path):
        """
        Индексирует проект.
        
        Args:
            project_path: Путь к проекту
        """
        # Запускаем индексацию в отдельном потоке
        self._run_async_task(self._index_project(project_path))
    
    async def _index_project(self, project_path):
        """
        Асинхронно индексирует проект.
        
        Args:
            project_path: Путь к проекту
        """
        try:
            logger.info(f"Indexing project: {project_path}")
            
            # Индексируем проект
            success = await self.orchestrator.index_project(project_path)
            
            # Отправляем сигнал о результате
            self.project_indexed.emit(success)
            
            logger.info(f"Project indexed: {success}")
        except Exception as e:
            logger.error(f"Error indexing project: {str(e)}")
            self.project_indexed.emit(False)
    
    @Slot(str, str, str, str)
    def create_specialized_agent(self, component_id, agent_id, agent_type, task_description):
        """
        Создает специализированного агента.
        
        Args:
            component_id: Идентификатор компонента интерфейса
            agent_id: Идентификатор агента
            agent_type: Тип агента (например, "coding", "browser_specialized", "react")
            task_description: Описание задачи
        """
        # Запускаем создание агента в отдельном потоке
        self._run_async_task(self._create_specialized_agent(component_id, agent_id, agent_type, task_description))
    
    async def _create_specialized_agent(self, component_id, agent_id, agent_type, task_description):
        """
        Асинхронно создает специализированного агента.
        
        Args:
            component_id: Идентификатор компонента интерфейса
            agent_id: Идентификатор агента
            agent_type: Тип агента
            task_description: Описание задачи
        """
        try:
            logger.info(f"Creating specialized agent {agent_id} of type {agent_type} for component {component_id}")
            
            # Создаем агента через оркестратор
            agent = await self.orchestrator.create_specialized_agent(agent_id, agent_type, task_description)
            
            if agent:
                # Регистрируем агента в контроллере агентов
                self.agent_controller.register_agent(component_id, agent)
                
                # Сохраняем связь между компонентом и агентом
                self.specialized_components[component_id] = agent_id
                
                # Если это браузерный агент, настраиваем дополнительные параметры
                if agent_type == "browser_specialized":
                    # Проверяем, связан ли компонент с браузером
                    browser_widget = self._find_browser_widget(component_id)
                    if browser_widget:
                        logger.info(f"Connecting browser specialized agent {agent_id} to browser widget")
                        # Здесь можно добавить дополнительную настройку для связи агента с браузером
                
                # Отправляем сигнал о создании агента
                self.agent_created.emit(agent_id)
                
                logger.info(f"Specialized agent {agent_id} created and registered for component {component_id}")
            else:
                logger.error(f"Failed to create specialized agent {agent_id}")
        except Exception as e:
            logger.error(f"Error creating specialized agent: {str(e)}")
            
    def _find_browser_widget(self, component_id):
        """
        Находит виджет браузера, связанный с компонентом.
        
        Args:
            component_id: Идентификатор компонента интерфейса
            
        Returns:
            QWidget: Виджет браузера или None, если не найден
        """
        try:
            # Пытаемся найти виджет браузера
            # 🚧 ЗАГЛУШКА! TODO_STUB: Требует реализации
            # Это заглушка, в реальном приложении нужно реализовать поиск виджета
            # по идентификатору компонента
            return None
        except Exception as e:
            logger.error(f"Error finding browser widget: {str(e)}")
            return None
    
    @Slot(str)
    def monitor_agent(self, component_id):
        """
        Мониторит агента и предоставляет руководство при необходимости.
        
        Args:
            component_id: Идентификатор компонента интерфейса
        """
        # Получаем идентификатор агента по идентификатору компонента
        agent_id = self.specialized_components.get(component_id)
        
        if not agent_id:
            logger.warning(f"No specialized agent found for component {component_id}")
            return
        
        # Запускаем мониторинг в отдельном потоке
        self._run_async_task(self._monitor_agent(component_id, agent_id))
    
    async def _monitor_agent(self, component_id, agent_id):
        """
        Асинхронно мониторит агента.
        
        Args:
            component_id: Идентификатор компонента интерфейса
            agent_id: Идентификатор агента
        """
        try:
            logger.info(f"Monitoring agent {agent_id} for component {component_id}")
            
            # Получаем агента
            agent = self.orchestrator.specialized_agents.get(agent_id)
            
            if not agent:
                logger.warning(f"Agent {agent_id} not found")
                self.agent_monitored.emit(agent_id, False)
                return
            
            # Получаем текущее состояние агента
            state = self.orchestrator._get_agent_state(agent)
            
            # Анализируем состояние и определяем, нужно ли руководство
            guidance = self.orchestrator._analyze_agent_state(state, agent_id)
            
            # Если нужно руководство, предоставляем его
            if guidance:
                logger.info(f"Providing guidance to agent {agent_id}: {guidance}")
                
                if hasattr(agent, "receive_guidance"):
                    await agent.receive_guidance(guidance)
                
                # Сохраняем руководство в Serena, если доступно
                if hasattr(self.orchestrator.agent_manager, "mcp_client") and self.orchestrator.agent_manager.mcp_client:
                    await self.orchestrator.store_agent_guidance(agent_id, {
                        "timestamp": self.orchestrator._get_timestamp(),
                        "state": state,
                        "guidance": guidance
                    })
                
                # Отправляем сигнал о мониторинге с руководством
                self.agent_monitored.emit(agent_id, True)
            else:
                # Отправляем сигнал о мониторинге без руководства
                self.agent_monitored.emit(agent_id, False)
                
            logger.info(f"Agent {agent_id} monitored successfully")
        except Exception as e:
            logger.error(f"Error monitoring agent: {str(e)}")
            self.agent_monitored.emit(agent_id, False)
    
    @Slot(str, str)
    def process_query_with_orchestration(self, component_id, query):
        """
        Обрабатывает запрос с оркестрацией.
        
        Args:
            component_id: Идентификатор компонента интерфейса
            query: Запрос для обработки
        """
        try:
            logger.info(f"Processing query with orchestration for component {component_id}: {query[:50]}...")
            
            # Получаем идентификатор агента по идентификатору компонента
            agent_id = self.specialized_components.get(component_id)
            
            if not agent_id:
                logger.warning(f"No specialized agent found for component {component_id}, using standard processing")
                # Используем стандартную обработку
                self.agent_controller.process_query(component_id, query)
                return
            
            # Запускаем мониторинг перед обработкой запроса
            self._run_async_task(self._monitor_before_query(component_id, agent_id, query))
        except Exception as e:
            logger.error(f"Error processing query with orchestration: {str(e)}")
            # Используем стандартную обработку в случае ошибки
            self.agent_controller.process_query(component_id, query)
    
    async def _monitor_before_query(self, component_id, agent_id, query):
        """
        Мониторит агента перед обработкой запроса.
        
        Args:
            component_id: Идентификатор компонента интерфейса
            agent_id: Идентификатор агента
            query: Запрос для обработки
        """
        try:
            # Мониторим агента
            await self._monitor_agent(component_id, agent_id)
            
            # Обрабатываем запрос
            self.agent_controller.process_query(component_id, query)
        except Exception as e:
            logger.error(f"Error monitoring before query: {str(e)}")
            # Используем стандартную обработку в случае ошибки
            self.agent_controller.process_query(component_id, query)
    
    def _run_async_task(self, coro):
        """
        Запускает асинхронную задачу в отдельном потоке.
        
        Args:
            coro: Корутина для выполнения
        """
        try:
            # Создаем новый event loop
            loop = asyncio.new_event_loop()
            
            # Запускаем корутину
            loop.run_until_complete(coro)
            
            # Закрываем loop
            loop.close()
        except Exception as e:
            logger.error(f"Error running async task: {str(e)}")

# Создаем глобальный экземпляр контроллера оркестрации
_orchestration_controller_instance = None

def get_orchestration_controller():
    """
    Возвращает глобальный экземпляр контроллера оркестрации.
    
    Returns:
        OrchestrationController: Экземпляр контроллера оркестрации
    """
    global _orchestration_controller_instance
    if _orchestration_controller_instance is None:
        _orchestration_controller_instance = OrchestrationController()
    return _orchestration_controller_instance
