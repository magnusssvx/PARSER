"""
Парсер текстовых файлов с судебными решениями.
Использует регулярные выражения для извлечения данных.
"""

import re  # Используем стандартный модуль re вместо regex
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from models.document import CourtDecision


class TextFileParser:
    """Парсер текстовых файлов с судебными решениями."""
    
    def __init__(self):
        # Регулярные выражения для поиска данных
        self.patterns = {
            'decision_number': [
                r'РЕШЕНИЕ\s*(?:от\s*\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4})?\s*(?:по делу\s*)?№?\s*([А-Яа-яA-Za-z0-9\-\/]+)',
                r'Решение\s*(?:от\s*\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4})?\s*(?:по делу\s*)?№?\s*([А-Яа-яA-Za-z0-9\-\/]+)',
                r'по делу\s*№?\s*([А-Яа-яA-Za-z0-9\-\/]+)',
                r'Дело\s*№?\s*([А-Яа-яA-Za-z0-9\-\/]+)',
            ],
            'decision_date': [
                r'от\s*(\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4})',
                r'(\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4})\s*г\.',
                r'дата\s*решения[:\s]*(\d{1,2}[\.\-]\d{1,2}[\.\-]\d{2,4})',
            ],
            'case_number': [
                r'по делу\s*№?\s*([А-Яа-яA-Za-z0-9\-\/]+)',
                r'дело\s*№?\s*([А-Яа-яA-Za-z0-9\-\/]+)',
                r'Дело\s*№?\s*([А-Яа-яA-Za-z0-9\-\/]+)',
                r'№\s*дела[:\s]*([А-Яа-яA-Za-z0-9\-\/]+)',
            ],
            'court_location': [
                r'АРБИТРАЖНЫЙ СУД\s+([А-Яа-я\s\-]+(?:области|края|республики|города|ГОРОДА))',
                r'Арбитражный суд\s+([А-Яа-я\s\-]+(?:области|края|республики|города))',
                r'([А-Яа-я\s\-]+(?:областной|краевой|городской|районный)\s+суд)',
            ],
            'judge': [
                r'Судья[:\s]*([А-Яа-яЁё\s\-\.]+)',
                r'Председательствующий[:\s]*([А-Яа-яЁё\s\-\.]+)',
                r'([А-Я][а-я]+\s+[А-Я][а-я]+(?:\s+[А-Я][а-я]+)?)\s+-\s+судья',
                r'в составе судьи\s+([А-Яа-яЁё\s\-\.]+)',
            ]
        }
        
    def parse_file(self, file_path: str) -> Optional[CourtDecision]:
        """Парсит один текстовый файл и возвращает объект CourtDecision."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Извлекаем данные с помощью регулярных выражений
            decision_number = self._extract_pattern(text, 'decision_number')
            date_str = self._extract_pattern(text, 'decision_date')
            case_number = self._extract_pattern(text, 'case_number')
            court_location = self._extract_pattern(text, 'court_location')
            judge = self._extract_pattern(text, 'judge')
            
            # Преобразуем дату
            decision_date = self._parse_date(date_str) if date_str else datetime.now()
            
            # Если не удалось извлечь судью, пытаемся найти в начале текста
            if not judge:
                judge = self._find_judge_in_text(text)
            
            # Если не удалось извлечь место суда, пытаемся найти в начале текста
            if not court_location or court_location == "Не указано":
                # Ищем в первых 200 символах
                first_lines = text[:200]
                court_match = re.search(r'АРБИТРАЖНЫЙ СУД\s+([^\n\r]+)', first_lines, re.IGNORECASE)
                if court_match:
                    court_location = court_match.group(1).strip()
                else:
                    court_location = "Не указано"
            
            return CourtDecision(
                decision_number=decision_number or "Не указан",
                decision_date=decision_date,
                case_number=case_number or "Не указан",
                court_location=court_location,
                judge=judge or "Не указан",
                full_text=text,
                source_file=file_path
            )
            
        except Exception as e:
            print(f"Ошибка при парсинге файла {file_path}: {e}")
            return None
    
    def parse_directory(self, directory_path: str) -> List[CourtDecision]:
        """Парсит все текстовые файлы в директории."""
        decisions = []
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"Директория {directory_path} не существует")
            return decisions
        
        # Ищем все текстовые файлы
        text_files = list(directory.glob("*.txt")) + list(directory.glob("*.doc")) + list(directory.glob("*.docx"))
        
        print(f"Найдено {len(text_files)} файлов для парсинга")
        
        for file_path in text_files:
            decision = self.parse_file(str(file_path))
            if decision:
                decisions.append(decision)
                print(f"Успешно распарсен файл: {file_path.name}")
            else:
                print(f"Не удалось распарсить файл: {file_path.name}")
        
        return decisions
    
    def _extract_pattern(self, text: str, pattern_type: str) -> Optional[str]:
        """Извлекает значение по регулярным выражениям."""
        for pattern in self.patterns[pattern_type]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result = match.group(1).strip()
                # Очищаем результат от лишних слов
                if pattern_type == 'decision_number':
                    # Убираем слова "от", "по", "делу" из номера решения
                    result = re.sub(r'^(от|по|делу)\s*', '', result, flags=re.IGNORECASE)
                return result
        return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Парсит дату из строки."""
        try:
            # Пробуем разные форматы даты
            formats = ['%d.%m.%Y', '%d-%m-%Y', '%d.%m.%y', '%d-%m-%y']
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # Если не удалось распарсить, возвращаем текущую дату
            return datetime.now()
        except Exception:
            return datetime.now()
    
    def _find_judge_in_text(self, text: str) -> Optional[str]:
        """Ищет имя судьи в тексте по характерным паттернам."""
        # Ищем ФИО в формате "Иванов И.И." или "Иванов Иван Иванович"
        patterns = [
            r'([А-Я][а-я]+(?:\s+[А-Я]\.){1,2})',
            r'([А-Я][а-я]+\s+[А-Я][а-я]+\s+[А-Я][а-я]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text[:1000])  # Ищем в начале текста
            if matches:
                # Берем первое найденное ФИО
                return matches[0].strip()
        
        return None