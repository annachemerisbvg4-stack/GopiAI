#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль специализированного агента с ограниченным контекстом.

Предоставляет реализацию агента, который фокусируется на конкретной задаче
и может получать руководство от оркестратора.
"""

from typing import Dict, Any

from pydantic import Field

from gopiai.app.agent.toolcall import ToolCallAgent
from gopiai.core.logging import get_logger
logger = get_logger().logger


class SpecializedAgent(ToolCallAgent):
    """
    Специализированный агент с ограниченным контекстом.
    
    Этот агент фокусируется на конкретной задаче и получает руководство от оркестратора.
    """
    
    name: str = "specialized"
    description: str = "Специализированный агент для выполнения конкретных задач"
    
    # Ограниченный контекст
    context: Dict[str, Any] = Field(default_factory=dict)
    
    # Флаг, указывающий, что агент работает с ограниченным контекстом
    is_limited_context: bool = True
    
    # Идентификатор для связи с оркестратором
    orchestrator_id: str = None
    
    # История руководства от оркестратора
    # Инициализируется в __init__
    
    # Текущая задача
    current_task: str = None
    
    # История действий
    def __init__(self, **data):
        super().__init__(**data)
        self.actions = []
        self.guidance_history = []
        self.memory = []
    
    async def set_context(self, context):
        """
        Устанавливает контекст для агента.
        
        Args:
            context: Контекст для агента
        """
        logger.info(f"Setting context for specialized agent: {self.name}")
        self.context = context
        
        # Если в контексте есть задача, устанавливаем ее
        if "task" in context:
            self.current_task = context["task"]
            
        # Добавляем информацию о контексте в системный промпт
        if self.system_prompt:
            context_info = (
                "Вы специализированный агент с ограниченным контекстом. "
                "Вы должны фокусироваться только на своей задаче и использовать "
                "только предоставленную информацию. Если вам нужна дополнительная "
                "информация, запросите ее у оркестратора."
            )
            
            # Добавляем информацию о задаче, если она есть
            if self.current_task:
                context_info += f"\n\nВаша текущая задача: {self.current_task}"
                
            # Добавляем информацию о релевантных файлах, если они есть
            if "relevant_files" in context and context["relevant_files"]:
                context_info += "\n\nРелевантные файлы для вашей задачи:"
                for file_path, file_info in context["relevant_files"].items():
                    summary = file_info.get("summary", "Нет описания")
                    context_info += f"\n- {file_path}: {summary}"
            
            # Обновляем системный промпт
            self.system_prompt = f"{self.system_prompt}\n\n{context_info}"
    
    async def receive_guidance(self, guidance):
        """
        Получает руководство от оркестратора.
        
        Args:
            guidance: Руководство от оркестратора
        """
        logger.info(f"Agent {self.name} received guidance: {guidance}")
        
        # Сохраняем руководство в истории
        self.guidance_history.append({
            "guidance": guidance,
            "timestamp": self._get_timestamp()
        })
        
        # Добавляем руководство в память агента
        if hasattr(self, "update_memory"):
            self.update_memory("system", f"GUIDANCE FROM ORCHESTRATOR: {guidance}")
        elif hasattr(self, "memory"):
            self.memory.append({
                "role": "system",
                "content": f"GUIDANCE FROM ORCHESTRATOR: {guidance}"
            })
    
    def _get_timestamp(self):
        """
        Возвращает текущую временную метку.
        
        Returns:
            str: Текущая временная метка
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def process(self, query):
        """
        Обрабатывает запрос с учетом ограниченного контекста.
        
        Args:
            query: Запрос для обработки
            
        Returns:
            str: Результат обработки запроса
        """
        # Если контекст ограничен, добавляем информацию о контексте в запрос
        if self.is_limited_context and self.context:
            # Создаем краткое описание контекста
            context_summary = self._create_context_summary()
            
            # Добавляем описание контекста к запросу
            enhanced_query = f"CONTEXT: {context_summary}\n\nQUERY: {query}"
            
            # Сохраняем действие
            self.actions.append(f"Processing query: {query[:50]}...")
            
            # Вызываем стандартную обработку с расширенным запросом
            return await super().process(enhanced_query)
        else:
            # Сохраняем действие
            self.actions.append(f"Processing query: {query[:50]}...")
            
            # Вызываем стандартную обработку
            return await super().process(query)
    
    def _create_context_summary(self):
        """
        Создает краткое описание контекста.
        
        Returns:
            str: Краткое описание контекста
        """
        summary = []
        
        # Добавляем информацию о задаче
        if "task" in self.context:
            summary.append(f"Task: {self.context['task']}")
        
        # Добавляем информацию о релевантных файлах
        if "relevant_files" in self.context and self.context["relevant_files"]:
            summary.append("Relevant files:")
            for file_path, file_info in list(self.context["relevant_files"].items())[:5]:  # Ограничиваем до 5 файлов
                summary.append(f"- {file_path}")
        
        # Добавляем информацию о зависимостях
        if "dependencies" in self.context and self.context["dependencies"]:
            summary.append("Dependencies:")
            for lang, deps in self.context["dependencies"].items():
                if isinstance(deps, list) and deps:
                    summary.append(f"- {lang}: {', '.join(deps[:3])}...")
                elif isinstance(deps, dict) and deps:
                    summary.append(f"- {lang}: {', '.join(list(deps.keys())[:3])}...")
        
        # Добавляем информацию об архитектуре
        if "architecture" in self.context and self.context["architecture"]:
            arch = self.context["architecture"]
            if "patterns" in arch and arch["patterns"]:
                summary.append(f"Architecture patterns: {', '.join(arch['patterns'])}")
        
        return "\n".join(summary)
    
    async def _handle_tool_call(self, tool_name, tool_args):
        """
        Обрабатывает вызов инструмента.
        
        Args:
            tool_name: Имя инструмента
            tool_args: Аргументы инструмента
            
        Returns:
            Any: Результат вызова инструмента
        """
        # Сохраняем действие
        self.actions.append(f"Using tool: {tool_name}")
        
        # Вызываем стандартную обработку
        return await super()._handle_tool_call(tool_name, tool_args)
    
    def get_current_state(self):
        """
        Возвращает текущее состояние агента.
        
        Returns:
            dict: Текущее состояние агента
        """
        state = {
            "name": self.name,
            "current_task": self.current_task,
            "actions": self.actions[-10:] if self.actions else [],  # Последние 10 действий
            "guidance_history": self.guidance_history[-5:] if self.guidance_history else [],  # Последние 5 руководств
            "timestamp": self._get_timestamp()
        }
        
        # Добавляем информацию о памяти, если она есть
        if hasattr(self, "memory") and self.memory:
            # Ограничиваем размер памяти для состояния
            memory_sample = self.memory[-5:] if isinstance(self.memory, list) else self.memory
            state["memory"] = memory_sample
        
        return state
