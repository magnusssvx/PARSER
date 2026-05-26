"""
Модель документа судебного решения.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CourtDecision:
    """Класс для хранения данных о судебном решении."""
    
    decision_number: str  # Номер решения
    decision_date: datetime  # Дата решения
    case_number: str  # Номер дела
    court_location: str  # Место принятия решения (город, область)
    judge: str  # Судья
    full_text: str  # Полный текст решения
    source_file: Optional[str] = None  # Исходный файл (если парсим из файла)
    url: Optional[str] = None  # URL (если парсим с сайта)
    
    def to_dict(self) -> dict:
        """Преобразует объект в словарь для сохранения в БД."""
        return {
            'decision_number': self.decision_number,
            'decision_date': self.decision_date,
            'case_number': self.case_number,
            'court_location': self.court_location,
            'judge': self.judge,
            'full_text': self.full_text,
            'source_file': self.source_file,
            'url': self.url
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CourtDecision':
        """Создает объект из словаря."""
        return cls(
            decision_number=data.get('decision_number', ''),
            decision_date=data.get('decision_date'),
            case_number=data.get('case_number', ''),
            court_location=data.get('court_location', ''),
            judge=data.get('judge', ''),
            full_text=data.get('full_text', ''),
            source_file=data.get('source_file'),
            url=data.get('url')
        )
    
    def __str__(self) -> str:
        """Строковое представление объекта."""
        return (f"Решение №{self.decision_number} от {self.decision_date.strftime('%d.%m.%Y')}\n"
                f"Дело №{self.case_number}\n"
                f"Суд: {self.court_location}\n"
                f"Судья: {self.judge}\n"
                f"Текст: {self.full_text[:100]}...")