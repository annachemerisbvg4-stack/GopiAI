import unittest
from unittest.mock import MagicMock
import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass

class EmotionalState(Enum):
    """Основные эмоциональные состояния"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONFUSED = "confused"
    ANGRY = "angry"
    SUPPORTIVE_NEEDED = "supportive_needed"


@dataclass
class EmotionalAnalysis:
    """Результат эмоционального анализа"""
    primary_emotion: EmotionalState
    confidence: float  # 0.0 - 1.0
    secondary_emotions: List[EmotionalState]
    emotional_intensity: float  # 0.0 - 1.0
    needs_support: bool
    crisis_indicators: List[str]
    recommendations: List[str]


class EmotionalClassifier:
    """
    Классификатор эмоций для диалогов с AI
    
    Анализирует эмоциональное состояние пользователя и предоставляет
    рекомендации для адаптации ответов AI под текущее настроение.
    """
    
    def __init__(self, ai_router):
        """
        Инициализирует EmotionalClassifier
        
        Args:
            ai_router: AI Router для выполнения анализа
        """
        self.ai_router = ai_router
        self.logger = logging.getLogger(__name__)
        
        # Критерии для различных типов эмоций
        self.emotion_criteria = {
            EmotionalState.POSITIVE: {
                "keywords": ["рад", "счастлив", "отлично", "замечательно", "восхитительно", "благодарен"],
                "patterns": ["как здорово", "очень доволен", "прекрасно работает"],
                "description": "Положительные эмоции: радость, удовлетворение, благодарность"
            },
            EmotionalState.NEGATIVE: {
                "keywords": ["грустно", "плохо", "ужасно", "расстроен", "печально", "тяжело"],
                "patterns": ["не могу больше", "все плохо", "ничего не получается"],
                "description": "Негативные эмоции: грусть, разочарование, печаль"
            },
            EmotionalState.FRUSTRATED: {
                "keywords": ["раздражает", "бесит", "достало", "надоело", "злит", "фрустрирует"],
                "patterns": ["не работает как надо", "уже сколько раз", "почему не получается"],
                "description": "Фрустрация: раздражение от неудач или препятствий"
            },
            EmotionalState.ANXIOUS: {
                "keywords": ["беспокоюсь", "тревожно", "волнуюсь", "страшно", "нервничаю"],
                "patterns": ["что если", "боюсь что", "а вдруг"],
                "description": "Тревога: беспокойство о будущем или неопределенности"
            },
            EmotionalState.CONFUSED: {
                "keywords": ["не понимаю", "запутался", "сложно", "непонятно", "как это"],
                "patterns": ["объясни еще раз", "не могу разобраться", "что это значит"],
                "description": "Замешательство: недопонимание или неясность"
            },
            EmotionalState.SUPPORTIVE_NEEDED: {
                "keywords": ["помоги", "поддержи", "трудно", "одиноко", "тяжелый период"],
                "patterns": ["нужна поддержка", "чувствую себя", "справиться самому"],
                "description": "Потребность в поддержке: просьба о помощи или понимании"
            }
        }
        
        # Кризисные индикаторы (требуют особого внимания)
        self.crisis_indicators = {
            "suicidal": ["не хочу жить", "покончить с собой", "суицид", "самоубийство"],
            "self_harm": ["причинить себе боль", "самоповреждение", "порезать себя"],
            "severe_depression": ["жизнь не имеет смысла", "все бесполезно", "никто не поймет"],
            "panic": ["паническая атака", "не могу дышать", "сердце бешено бьется"],
            "abuse": ["бьет меня", "насилие", "угрожает", "причиняет боль"]
        }
        
        self.logger.info("EmotionalClassifier инициализирован")
    
    def analyze_emotional_state(self, conversation_history: List[Dict], current_message: str) -> EmotionalAnalysis:
        """
        Анализирует эмоциональное состояние на основе сообщения и истории диалога
        
        Args:
            conversation_history: История диалога [{"role": "user/assistant", "content": "..."}]
            current_message: Текущее сообщение для анализа
            
        Returns:
            EmotionalAnalysis: Результат анализа эмоций
        """
        try:
            # 1. Быстрая эвристическая оценка
            heuristic_result = self._heuristic_emotion_detection(current_message)
            
            # 2. Детальный анализ через AI
            ai_result = self._ai_emotion_analysis(conversation_history, current_message)
            
            # 3. Проверка кризисных индикаторов
            crisis_indicators = self._detect_crisis_indicators(current_message)
            
            # 4. Объединение результатов
            final_analysis = self._combine_analysis_results(
                heuristic_result, ai_result, crisis_indicators
            )
            
            self.logger.info(f"Эмоциональный анализ завершен: {final_analysis.primary_emotion.value} (confidence: {final_analysis.confidence:.2f})")
            
            return final_analysis
            
        except Exception as e:
            self.logger.error(f"Ошибка при анализе эмоций: {e}")
            # Возвращаем нейтральный результат при ошибке
            return EmotionalAnalysis(
                primary_emotion=EmotionalState.NEUTRAL,
                confidence=0.5,
                secondary_emotions=[],
                emotional_intensity=0.5,
                needs_support=False,
                crisis_indicators=[],
                recommendations=["Продолжить диалог в обычном режиме"]
            )
    
    def _heuristic_emotion_detection(self, message: str) -> Dict[str, Any]:
        """
        Быстрое эвристическое определение эмоций по ключевым словам
        
        Args:
            message: Сообщение для анализа
            
        Returns:
            Dict: Результат эвристического анализа
        """
        message_lower = message.lower()
        detected_emotions = {}
        
        for emotion, criteria in self.emotion_criteria.items():
            score = 0.0
            
            # Проверяем ключевые слова
            for keyword in criteria["keywords"]:
                if keyword in message_lower:
                    score += 0.3
            
            # Проверяем паттерны
            for pattern in criteria["patterns"]:
                if pattern in message_lower:
                    score += 0.5
            
            if score > 0:
                detected_emotions[emotion] = min(score, 1.0)
        
        # Опре��еляем доминирующую эмоцию
        if detected_emotions:
            primary_emotion = max(detected_emotions.items(), key=lambda x: x[1])
            return {
                "primary_emotion": primary_emotion[0],
                "confidence": primary_emotion[1],
                "all_emotions": detected_emotions
            }
        else:
            return {
                "primary_emotion": EmotionalState.NEUTRAL,
                "confidence": 0.7,
                "all_emotions": {EmotionalState.NEUTRAL: 0.7}
            }
    
    def _ai_emotion_analysis(self, conversation_history: List[Dict], current_message: str) -> Dict[str, Any]:
        """
        Детальный анализ эмоций через AI (адаптированный промпт от OpenAI)
        
        Args:
            conversation_history: История диалога
            current_message: Текущее сообщение
            
        Returns:
            Dict: Результат AI анализа
        """
        try:
            # Формируем контекст диалога
            conversation_