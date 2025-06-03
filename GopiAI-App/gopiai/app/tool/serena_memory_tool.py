#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Инструмент для работы с памятью Serena.

Предоставляет функциональность для чтения, записи и управления
данными в памяти Serena.
"""

from gopiai.app.agent.agent_manager import AgentManager
from gopiai.core.logging import get_logger
logger = get_logger().logger
from gopiai.app.tool.base import BaseTool, ToolResult


class SerenaMemoryTool(BaseTool):
    """Инструмент для работы с памятью Serena."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="serena_memory",
            description="Работает с памятью Serena для хранения и извлечения данных",
            function=self._execute,
            parameters={
                "action": {
                    "type": "string",
                    "description": "Действие: read, write, list",
                    "enum": ["read", "write", "list"]
                },
                "file_name": {
                    "type": "string",
                    "description": "Имя файла в памяти Serena"
                },
                "content": {
                    "type": "string",
                    "description": "Содержимое для записи (только для action=write)"
                }
            },
            required_params=["action"]
        )
    
    async def _execute(self, action, file_name=None, content=None) -> ToolResult:
        """
        Выполняет операцию с памятью Serena.
        
        Args:
            action: Действие (read, write, list)
            file_name: Имя файла в памяти Serena
            content: Содержимое для записи
            
        Returns:
            ToolResult: Результат операции
        """
        agent_manager = AgentManager.instance()
        
        if not hasattr(agent_manager, "mcp_client") or not agent_manager.mcp_client:
            return ToolResult(
                success=False,
                message="MCP client not available",
                data={"error": "MCP client not available"}
            )
            
        try:
            if action == "read":
                if not file_name:
                    return ToolResult(
                        success=False,
                        message="File name is required for read action",
                        data={"error": "File name is required"}
                    )
                
                result = await agent_manager.mcp_client.serena_read_memory(file_name)
                
                if result:
                    return ToolResult(
                        success=True,
                        message=f"Successfully read file {file_name}",
                        data={"content": result}
                    )
                else:
                    return ToolResult(
                        success=False,
                        message=f"File {file_name} not found or empty",
                        data={"error": "File not found or empty"}
                    )
                    
            elif action == "write":
                if not file_name:
                    return ToolResult(
                        success=False,
                        message="File name is required for write action",
                        data={"error": "File name is required"}
                    )
                
                if not content:
                    return ToolResult(
                        success=False,
                        message="Content is required for write action",
                        data={"error": "Content is required"}
                    )
                
                result = await agent_manager.mcp_client.serena_write_memory(file_name, content)
                
                if result:
                    return ToolResult(
                        success=True,
                        message=f"Successfully wrote to file {file_name}",
                        data={"file_name": file_name}
                    )
                else:
                    return ToolResult(
                        success=False,
                        message=f"Failed to write to file {file_name}",
                        data={"error": "Write operation failed"}
                    )
                    
            elif action == "list":
                result = await agent_manager.mcp_client.serena_list_memory()
                
                if result:
                    return ToolResult(
                        success=True,
                        message="Successfully listed memory files",
                        data={"files": result}
                    )
                else:
                    return ToolResult(
                        success=False,
                        message="Failed to list memory files",
                        data={"error": "List operation failed"}
                    )
                    
            else:
                return ToolResult(
                    success=False,
                    message=f"Unknown action: {action}",
                    data={"error": f"Unknown action: {action}"}
                )
                
        except Exception as e:
            logger.error(f"Error executing Serena memory tool: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Error: {str(e)}",
                data={"error": str(e)}
            )

class ProjectContextTool(BaseTool):
    """Инструмент для работы с контекстом проекта."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="project_context",
            description="Получает информацию о контексте проекта",
            function=self._execute,
            parameters={
                "action": {
                    "type": "string",
                    "description": "Действие: get_files, get_dependencies, get_architecture, get_all",
                    "enum": ["get_files", "get_dependencies", "get_architecture", "get_all"]
                },
                "project_path": {
                    "type": "string",
                    "description": "Путь к проекту (опционально)"
                }
            },
            required_params=["action"]
        )
    
    async def _execute(self, action, project_path=None) -> ToolResult:
        """
        Выполняет операцию с контекстом проекта.
        
        Args:
            action: Действие
            project_path: Путь к проекту
            
        Returns:
            ToolResult: Результат операции
        """
        try:
            # Импортируем оркестратор
            from gopiai.app.agent.orchestrator import get_orchestrator
            
            orchestrator = get_orchestrator()
            
            # Если проект не проиндексирован, индексируем его
            if not orchestrator.project_context and project_path:
                await orchestrator.index_project(project_path)
            
            # Если контекст все еще пуст, пытаемся загрузить его из Serena
            if not orchestrator.project_context and orchestrator.project_path:
                context = await orchestrator.retrieve_project_context(orchestrator.project_path)
                if context:
                    orchestrator.project_context = context
            
            # Если контекст все еще пуст, возвращаем ошибку
            if not orchestrator.project_context:
                return ToolResult(
                    success=False,
                    message="Project context not available",
                    data={"error": "Project context not available"}
                )
            
            if action == "get_files":
                return ToolResult(
                    success=True,
                    message="Successfully retrieved project files",
                    data={"files": orchestrator.project_context.get("files", {})}
                )
                
            elif action == "get_dependencies":
                return ToolResult(
                    success=True,
                    message="Successfully retrieved project dependencies",
                    data={"dependencies": orchestrator.project_context.get("dependencies", {})}
                )
                
            elif action == "get_architecture":
                return ToolResult(
                    success=True,
                    message="Successfully retrieved project architecture",
                    data={"architecture": orchestrator.project_context.get("architecture", {})}
                )
                
            elif action == "get_all":
                return ToolResult(
                    success=True,
                    message="Successfully retrieved project context",
                    data=orchestrator.project_context
                )
                
            else:
                return ToolResult(
                    success=False,
                    message=f"Unknown action: {action}",
                    data={"error": f"Unknown action: {action}"}
                )
                
        except Exception as e:
            logger.error(f"Error executing Project Context tool: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Error: {str(e)}",
                data={"error": str(e)}
            )

class OrchestratorTool(BaseTool):
    """Инструмент для взаимодействия с оркестратором агентов."""
    
    def __init__(self):
        """Инициализирует инструмент."""
        super().__init__(
            name="orchestrator",
            description="Взаимодействует с оркестратором агентов",
            function=self._execute,
            parameters={
                "action": {
                    "type": "string",
                    "description": "Действие: create_agent, monitor_agent, get_guidance",
                    "enum": ["create_agent", "monitor_agent", "get_guidance"]
                },
                "agent_id": {
                    "type": "string",
                    "description": "Идентификатор агента"
                },
                "agent_type": {
                    "type": "string",
                    "description": "Тип агента (только для create_agent): coding, browser_specialized, react, etc."
                },
                "task_description": {
                    "type": "string",
                    "description": "Описание задачи (только для create_agent)"
                }
            },
            required_params=["action", "agent_id"]
        )
    
    async def _execute(self, action, agent_id, agent_type=None, task_description=None) -> ToolResult:
        """
        Выполняет операцию с оркестратором.
        
        Args:
            action: Действие
            agent_id: Идентификатор агента
            agent_type: Тип агента
            task_description: Описание задачи
            
        Returns:
            ToolResult: Результат операции
        """
        try:
            # Импортируем оркестратор
            from gopiai.app.agent.orchestrator import get_orchestrator
            
            orchestrator = get_orchestrator()
            
            if action == "create_agent":
                if not agent_type:
                    return ToolResult(
                        success=False,
                        message="Agent type is required for create_agent action",
                        data={"error": "Agent type is required"}
                    )
                
                if not task_description:
                    return ToolResult(
                        success=False,
                        message="Task description is required for create_agent action",
                        data={"error": "Task description is required"}
                    )
                
                agent = await orchestrator.create_specialized_agent(agent_id, agent_type, task_description)
                
                if agent:
                    return ToolResult(
                        success=True,
                        message=f"Successfully created agent {agent_id}",
                        data={"agent_id": agent_id, "agent_type": agent_type}
                    )
                else:
                    return ToolResult(
                        success=False,
                        message=f"Failed to create agent {agent_id}",
                        data={"error": "Agent creation failed"}
                    )
                    
            elif action == "monitor_agent":
                result = await orchestrator.monitor_agent(agent_id)
                
                if result:
                    return ToolResult(
                        success=True,
                        message=f"Successfully monitored agent {agent_id}",
                        data={"agent_id": agent_id}
                    )
                else:
                    return ToolResult(
                        success=False,
                        message=f"Failed to monitor agent {agent_id}",
                        data={"error": "Agent monitoring failed"}
                    )
                    
            elif action == "get_guidance":
                agent = orchestrator.specialized_agents.get(agent_id)
                
                if not agent:
                    return ToolResult(
                        success=False,
                        message=f"Agent {agent_id} not found",
                        data={"error": "Agent not found"}
                    )
                
                if hasattr(agent, "guidance_history") and agent.guidance_history:
                    return ToolResult(
                        success=True,
                        message=f"Successfully retrieved guidance for agent {agent_id}",
                        data={"guidance_history": agent.guidance_history}
                    )
                else:
                    return ToolResult(
                        success=True,
                        message=f"No guidance found for agent {agent_id}",
                        data={"guidance_history": []}
                    )
                    
            else:
                return ToolResult(
                    success=False,
                    message=f"Unknown action: {action}",
                    data={"error": f"Unknown action: {action}"}
                )
                
        except Exception as e:
            logger.error(f"Error executing Orchestrator tool: {str(e)}")
            return ToolResult(
                success=False,
                message=f"Error: {str(e)}",
                data={"error": str(e)}
            )

# Функция для получения всех инструментов оркестрации
def get_orchestration_tools():
    """
    Возвращает список инструментов для оркестрации.
    
    Returns:
        list: Список инструментов
    """
    return [
        SerenaMemoryTool(),
        ProjectContextTool(),
        OrchestratorTool()
    ]
