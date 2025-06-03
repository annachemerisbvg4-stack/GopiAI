"""
Заглушка для gopiai.app.config.
STUB: Используется временно для избежания циклических зависимостей.
"""

# STUB: Минимальная заглушка для config
class Config:
    def __init__(self):
        self.data = {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value

# Создаем экземпляр конфигурации
config = Config()

__all__ = ['config']
