"""
AutoGen Core - Ядро мультиагентной системы для GopiAI
"""

import os
import random
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Проверяем наличие AutoGen
AUTOGEN_AVAILABLE = False
ConversableAgent = None
AssistantAgent = None  
UserProxyAgent = None

# Пробуем различные варианты импорта AutoGen
import_attempts = [
    # Попытка 1: Стандартный импорт
    lambda: __import__('autogen', fromlist=['ConversableAgent', 'AssistantAgent', 'UserProxyAgent']),
    # Попытка 2: Из agentchat
    lambda: __import__('autogen.agentchat', fromlist=['ConversableAgent', 'AssistantAgent', 'UserProxyAgent']),
    # Попытка 3: Прямой импорт модулей
    lambda: (
        __import__('autogen.agentchat.conversable_agent', fromlist=['ConversableAgent']),
        __import__('autogen.agentchat.assistant_agent', fromlist=['AssistantAgent']),
        __import__('autogen.agentchat.user_proxy_agent', fromlist=['UserProxyAgent'])
    )
]

for i, attempt in enumerate(import_attempts, 1):
    try:
        print(f"🔄 Попытка импорта AutoGen #{i}...")
        
        if i == 1:  # Стандартный импорт
            autogen_module = attempt()
            ConversableAgent = getattr(autogen_module, 'ConversableAgent', None)
            AssistantAgent = getattr(autogen_module, 'AssistantAgent', None)
            UserProxyAgent = getattr(autogen_module, 'UserProxyAgent', None)
            
        elif i == 2:  # Из agentchat
            agentchat_module = attempt()
            ConversableAgent = getattr(agentchat_module, 'ConversableAgent', None)
            AssistantAgent = getattr(agentchat_module, 'AssistantAgent', None)
            UserProxyAgent = getattr(agentchat_module, 'UserProxyAgent', None)
            
        elif i == 3:  # Прямой импорт
            conv_module, assist_module, proxy_module = attempt()
            ConversableAgent = getattr(conv_module, 'ConversableAgent', None)
            AssistantAgent = getattr(assist_module, 'AssistantAgent', None)
            UserProxyAgent = getattr(proxy_module, 'UserProxyAgent', None)
        
        # Проверяем, что все классы загружены
        if ConversableAgent and AssistantAgent and UserProxyAgent:
            AUTOGEN_AVAILABLE = True
            print(f"✅ AutoGen импортирован успешно (попытка #{i})")
            break
        else:
            print(f"⚠️ Попытка #{i}: Не все классы найдены")
            
    except ImportError as e:
        print(f"⚠️ Попытка #{i} неудачна: {e}")
        continue
    except Exception as e:
        print(f"❌ Ошибка при попытке #{i}: {e}")
        continue

# Если AutoGen недоступен, создаем заглушки
if not AUTOGEN_AVAILABLE:
    print("⚠️ AutoGen не найден. Создаем заглушки...")
    print("💡 Для установки выполните: pip install 'pyautogen[cerebras]' или pip install pyautogen")
    
    class MockAgent:
        """Заглушка для AutoGen агентов"""
        def __init__(self, *args, **kwargs):
            self.name = kwargs.get('name', 'MockAgent')
            print(f"⚠️ Создана заглушка агента: {self.name}")
        
        def initiate_chat(self, *args, **kwargs):
            return {"chat_history": [{"name": self.name, "content": "AutoGen недоступен"}]}
    
    ConversableAgent = MockAgent
    AssistantAgent = MockAgent
    UserProxyAgent = MockAgent

class AutoGenConfig:
    """Конфигурация для AutoGen агентов"""
    
    # 📊 Модели Cerebras с лимитами Free Tier
    CEREBRAS_MODELS = [
        {
            "model": "llama3.1-8b",
            "api_key": os.environ.get("CEREBRAS_API_KEY"),
            "api_type": "cerebras"
            # Лимиты: 30 req/min, 900 req/hour, 14400 req/day, 60k tokens/min
        },
        {
            "model": "llama-3.3-70b", 
            "api_key": os.environ.get("CEREBRAS_API_KEY"),
            "api_type": "cerebras"
            # Лимиты: 30 req/min, 900 req/hour, 14400 req/day, 60k tokens/min
        },
        {
            "model": "llama-4-scout-17b-16e-instruct",
            "api_key": os.environ.get("CEREBRAS_API_KEY"),
            "api_type": "cerebras"
            # Лимиты: 30 req/min, 900 req/hour, 14400 req/day, 60k tokens/min
        },
        {
            "model": "qwen-3-32b",
            "api_key": os.environ.get("CEREBRAS_API_KEY"),
            "api_type": "cerebras"
            # Лимиты: 30 req/min, 900 req/hour, 14400 req/day, 60k tokens/min
        }
    ]
    
    # 🔄 Запасная конфигурация OpenAI
    OPENAI_CONFIG = [
        {
            "model": "gpt-4o-mini",
            "api_key": os.environ.get("OPENAI_API_KEY"),
            "api_type": "openai"
        }
    ]
    
    @classmethod
    def get_config_list(cls, strategy: str = "best_first") -> List[Dict[str, Any]]:
        """
        Получает конфигурацию моделей по стратегии
        
        Args:
            strategy: Стратегия выбора ("best_first", "random", "all_rotation", "openai_fallback")
        
        Returns:
            Список конфигураций моделей
        """
        if strategy == "random":
            return [random.choice(cls.CEREBRAS_MODELS)]
        elif strategy == "best_first":
            return [cls.CEREBRAS_MODELS[1]]  # llama-3.3-70b
        elif strategy == "all_rotation":
            return cls.CEREBRAS_MODELS
        elif strategy == "openai_fallback":
            return cls.OPENAI_CONFIG
        else:
            return [cls.CEREBRAS_MODELS[0]]  # Дефолт

class AutoGenAgent:
    """Обертка для AutoGen агентов"""
    
    def __init__(self, name: str, role: str = "assistant", strategy: str = "best_first"):
        """
        Инициализация агента
        
        Args:
            name: Имя агента
            role: Роль агента ("assistant" или "user_proxy")
            strategy: Стратегия выбора модели
        """
        self.name = name
        self.role = role
        self.strategy = strategy
        self.agent = None
        
        if not AUTOGEN_AVAILABLE:
            print(f"⚠️ Невозможно создать агента {name}: AutoGen недоступен")
            return
            
        self._create_agent()
    
    def _create_agent(self):
        """Создает AutoGen агента"""
        try:
            config_list = AutoGenConfig.get_config_list(self.strategy)
            
            if self.role == "assistant":
                try:
                    # Проверяем доступность ConversableAgent
                    if ConversableAgent is None:
                        raise NameError("ConversableAgent недоступен")
                    # Пробуем новый API
                    self.agent = ConversableAgent(
                        name=self.name,
                        llm_config={"config_list": config_list},
                        system_message="Ты полезный ассистент в системе GopiAI. Отвечай кратко и по делу.",
                        human_input_mode="NEVER"
                    )
                except NameError:
                    # Проверяем доступность AssistantAgent
                    if AssistantAgent is None:
                        raise Exception("Классы агентов недоступны - AutoGen не установлен")
                    # Fallback на старый API
                    self.agent = AssistantAgent(
                        name=self.name,
                        llm_config={"config_list": config_list},
                        system_message="Ты полезный ассистент в системе GopiAI. Отвечай кратко и по делу."
                    )
            elif self.role == "user_proxy":
                try:
                    # Проверяем доступность ConversableAgent
                    if ConversableAgent is None:
                        raise NameError("ConversableAgent недоступен")
                    # Пробуем новый API
                    self.agent = ConversableAgent(
                        name=self.name,
                        llm_config=False,
                        human_input_mode="NEVER",
                        max_consecutive_auto_reply=1,
                        code_execution_config=False
                    )
                except NameError:
                    # Проверяем доступность UserProxyAgent
                    if UserProxyAgent is None:
                        raise Exception("Классы агентов недоступны - AutoGen не установлен")
                    # Fallback на старый API
                    self.agent = UserProxyAgent(
                        name=self.name,
                        human_input_mode="NEVER",
                        max_consecutive_auto_reply=1,
                        code_execution_config=False
                    )
            
            print(f"✅ Агент {self.name} создан успешно")
        except Exception as e:
            print(f"❌ Ошибка создания агента {self.name}: {e}")
    
    def chat(self, message: str, recipient_agent: 'AutoGenAgent') -> Optional[Any]:
        """
        Начинает чат с другим агентом
        
        Args:
            message: Сообщение для отправки
            recipient_agent: Агент-получатель
        
        Returns:
            Результат чата или None в случае ошибки
        """
        if not self.agent or not recipient_agent.agent:
            print("❌ Один из агентов недоступен")
            return None
        
        try:
            if self.role == "user_proxy":
                result = self.agent.initiate_chat(recipient_agent.agent, message=message)
                return result
            else:
                print("❌ Только user_proxy агенты могут инициировать чат")
                return None
        except Exception as e:
            print(f"❌ Ошибка в чате: {e}")
            return None

class AutoGenManager:
    """Менеджер для управления AutoGen агентами"""
    
    def __init__(self):
        self.agents = {}
        self.is_available = AUTOGEN_AVAILABLE
    
    def create_agent(self, name: str, role: str = "assistant", strategy: str = "best_first") -> Optional[AutoGenAgent]:
        """
        Создает и регистрирует нового агента
        
        Args:
            name: Имя агента
            role: Роль агента
            strategy: Стратегия выбора модели
        
        Returns:
            Созданный агент или None
        """
        if not self.is_available:
            print("⚠️ AutoGen недоступен")
            return None
        
        agent = AutoGenAgent(name, role, strategy)
        if agent.agent:
            self.agents[name] = agent
            return agent
        return None
    
    def get_agent(self, name: str) -> Optional[AutoGenAgent]:
        """Получает агента по имени"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """Возвращает список имен агентов"""
        return list(self.agents.keys())
    
    def simple_chat(self, message: str, strategy: str = "best_first") -> Optional[str]:
        """
        Простой чат с автоматически созданными агентами
        
        Args:
            message: Сообщение для отправки
            strategy: Стратегия выбора модели
        
        Returns:
            Ответ ассистента или None
        """
        if not self.is_available:
            return "❌ AutoGen недоступен"
        
        try:
            # Создаем временных агентов
            user_agent = AutoGenAgent("User", "user_proxy", strategy)
            assistant_agent = AutoGenAgent("Assistant", "assistant", strategy)
            
            if not user_agent.agent or not assistant_agent.agent:
                return "❌ Не удалось создать агентов"
            
            # Запускаем чат
            result = user_agent.chat(message, assistant_agent)
            
            # Извлекаем последний ответ ассистента
            if result and hasattr(result, 'chat_history') and result.chat_history:
                for msg in reversed(result.chat_history):
                    if msg.get('name') == 'Assistant':
                        return msg.get('content', 'Нет ответа')
            
            return "Нет ответа от ассистента"
        except Exception as e:
            return f"❌ Ошибка в чате: {e}"

# Глобальный экземпляр менеджера
autogen_manager = AutoGenManager()