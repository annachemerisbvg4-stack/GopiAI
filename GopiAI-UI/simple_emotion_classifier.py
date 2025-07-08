"""
Упрощенный эмоциональный классификатор для тестирования

Этот модуль предоставляет базовую реализацию анализа эмоций без зависимостей от crewai.
"""

import random
from typing import Dict, Any

class SimpleEmotionClassifier:
    """Упрощенный классификатор эмоций для тестирования"""
    
    def __init__(self):
        """Инициализация классификатора"""
        self.emotions = ["happy", "sad", "angry", "surprised", "neutral"]
        self.sentiments = ["positive", "neutral", "negative"]
        
    def analyze_emotion(self, text: str) -> Dict[str, Any]:
        """
        Анализирует эмоциональную окраску текста
        
        Args:
            text (str): Текст для анализа
            
        Returns:
            Dict[str, Any]: Словарь с результатами анализа
        """
        if not text or not isinstance(text, str):
            return self._create_result("neutral", 0.5, "neutral")
            
        text = text.lower()
        
        # Простые эвристики для демонстрации
        emotion = "neutral"
        confidence = random.uniform(0.7, 0.99)  # Случайная уверенность для тестирования
        
        if any(word in text for word in ["рад", "счастлив", "отлично", "прекрасно", "ура"]):
            emotion = "happy"
        elif any(word in text for word in ["грустно", "плохо", "печально", "ужасно"]):
            emotion = "sad"
        elif any(word in text for word in ["злой", "сердит", "бесит", "раздражает"]):
            emotion = "angry"
        elif any(word in text for word in ["вау", "ого", "невероятно", "удивительно"]):
            emotion = "surprised"
            
        # Определение сентимента
        if emotion in ["happy", "surprised"]:
            sentiment = "positive"
        elif emotion in ["sad", "angry"]:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        return self._create_result(emotion, confidence, sentiment)
    
    def _create_result(self, emotion: str, confidence: float, sentiment: str) -> Dict[str, Any]:
        """Создает словарь с результатами анализа"""
        return {
            "emotion": emotion,
            "confidence": confidence,
            "sentiment": sentiment,
            "is_positive": sentiment == "positive",
            "is_negative": sentiment == "negative",
            "is_neutral": sentiment == "neutral"
        }

# Создаем глобальный экземпляр для импорта
emotion_classifier = SimpleEmotionClassifier()

def get_emotion_classifier():
    """Фабричная функция для получения экземпляра классификатора"""
    return emotion_classifier
