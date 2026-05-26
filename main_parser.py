"""
Основной скрипт для запуска проекта парсинга судебных решений.
"""

import os
import sys
from datetime import datetime


def print_banner():
    """Выводит баннер проекта."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║         ПАРСЕР СУДЕБНЫХ РЕШЕНИЙ - СИСТЕМА УПРАВЛЕНИЯ     ║
    ╚══════════════════════════════════════════════════════════╝
    
    Основные функции:
    1. Парсинг текстовых файлов с решениями
    2. Сохранение данных в базу данных
    3. Поиск и анализ решений
    4. Экспорт данных
    
    Автор: Студенческий проект
    Версия: 1.0.0
    """
    print(banner)


def parse_files_menu():
    """Меню парсинга файлов."""
    from parsers.text_parser import TextFileParser
    
    print("\n" + "="*60)
    print("ПАРСИНГ ФАЙЛОВ С СУДЕБНЫМИ РЕШЕНИЯМИ")
    print("="*60)
    
    # Проверяем наличие папки с данными
    data_dir = "parsed_decisions"
    if not os.path.exists(data_dir):
        print(f"Папка '{data_dir}' не найдена.")
        print("Создайте папку и добавьте в неё текстовые файлы с решениями.")
        return
    
    # Показываем файлы в папке
    files = [f for f in os.listdir(data_dir) if f.endswith(('.txt', '.doc', '.docx'))]
    
    if not files:
        print(f"В папке '{data_dir}' нет текстовых файлов.")
        print("Добавьте файлы для парсинга.")
        return
    
    print(f"Найдено файлов: {len(files)}")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file}")
    
    # Запускаем парсер
    print("\nЗапуск парсера...")
    parser = TextFileParser()
    decisions = parser.parse_directory(data_dir)
    
    print(f"\nРезультаты парсинга:")
    print(f"Успешно распарсено: {len(decisions)} из {len(files)} файлов")
    
    if decisions:
        print("\nПример распарсенных данных:")
        for i, decision in enumerate(decisions[:3], 1):  # Показываем первые 3
            print(f"\n{i}. Решение №{decision.decision_number}")
            print(f"   Дата: {decision.decision_date.strftime('%d.%m.%Y')}")
            print(f"   Дело: {decision.case_number}")
            print(f"   Суд: {decision.court_location}")
            print(f"   Судья: {decision.judge}")
    
    return decisions


def database_menu():
    """Меню работы с базой данных."""
    print("\n" + "="*60)
    print("РАБОТА С БАЗОЙ ДАННЫХ")
    print("="*60)
    
    print("Доступные функции:")
    print("1. Подключение к PostgreSQL")
    print("2. Подключение к ClickHouse")
    print("3. Сохранение данных в БД")
    print("4. Поиск решений")
    print("5. Статистика")
    print("0. Назад")
    
    choice = input("\nВыберите действие: ")
    
    if choice == "1":
        print("\nДля подключения к PostgreSQL требуется:")
        print("1. Установленный PostgreSQL")
        print("2. Созданная база данных 'court_decisions'")
        print("3. Учетные данные: host, port, username, password")
        print("\nИспользуйте database/db_manager.py для настройки.")
        
    elif choice == "2":
        print("\nДля подключения к ClickHouse требуется:")
        print("1. Установленный ClickHouse")
        print("2. Установленный clickhouse-sqlalchemy")
        print("3. Учетные данные для подключения")
        print("\nИспользуйте database/db_manager.py для настройки.")
        
    elif choice == "3":
        print("\nСохранение данных в БД...")
        # Здесь будет код сохранения
        
    elif choice == "4":
        print("\nПоиск решений...")
        # Здесь будет код поиска
        
    elif choice == "5":
        print("\nСтатистика...")
        # Здесь будет код статистики


def export_menu():
    """Меню экспорта данных."""
    print("\n" + "="*60)
    print("ЭКСПОРТ ДАННЫХ")
    print("="*60)
    
    print("Доступные форматы экспорта:")
    print("1. CSV файл")
    print("2. JSON файл")
    print("3. Excel файл")
    print("4. SQL дамп")
    print("0. Назад")
    
    choice = input("\nВыберите формат: ")
    
    if choice in ["1", "2", "3", "4"]:
        print(f"\nЭкспорт в выбранный формат будет реализован в следующей версии.")
        print("Для экспорта используйте функции из модуля export/")
    elif choice == "0":
        return
    else:
        print("Неверный выбор.")


def statistics_menu():
    """Меню статистики."""
    print("\n" + "="*60)
    print("СТАТИСТИКА И АНАЛИТИКА")
    print("="*60)
    
    print("Доступные отчеты:")
    print("1. Общая статистика по решениям")
    print("2. Статистика по судам")
    print("3. Статистика по судьям")
    print("4. Анализ временных периодов")
    print("5. Часто встречающиеся дела")
    print("0. Назад")
    
    choice = input("\nВыберите отчет: ")
    
    if choice in ["1", "2", "3", "4", "5"]:
        print(f"\nОтчет {choice} будет сгенерирован в следующей версии.")
        print("Для анализа используйте функции из модуля analytics/")
    elif choice == "0":
        return
    else:
        print("Неверный выбор.")


def test_project():
    """Запуск тестов проекта."""
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ПРОЕКТА")
    print("="*60)
    
    print("Доступные тесты:")
    print("1. Запуск всех тестов")
    print("2. Тестирование парсера")
    print("3. Тестирование базы данных")
    print("4. Демонстрация работы")
    print("0. Назад")
    
    choice = input("\nВыберите тест: ")
    
    if choice == "1":
        print("\nЗапуск всех тестов...")
        os.system("python run_tests.py")
        
    elif choice == "2":
        print("\nТестирование парсера...")
        os.system("python test_parser.py")
        
    elif choice == "3":
        print("\nТестирование базы данных...")
        os.system("python test_database.py")
        
    elif choice == "4":
        print("\nДемонстрация работы...")
        os.system("python run_tests.py demo")
        
    elif choice == "0":
        return
    else:
        print("Неверный выбор.")


def main():
    """Основная функция программы."""
    print_banner()
    
    while True:
        print("\n" + "="*60)
        print("ГЛАВНОЕ МЕНЮ")
        print("="*60)
        print("1. Парсинг файлов")
        print("2. Работа с базой данных")
        print("3. Экспорт данных")
        print("4. Статистика и аналитика")
        print("5. Тестирование проекта")
        print("6. О проекте")
        print("0. Выход")
        
        choice = input("\nВыберите действие: ")
        
        if choice == "1":
            parse_files_menu()
        elif choice == "2":
            database_menu()
        elif choice == "3":
            export_menu()
        elif choice == "4":
            statistics_menu()
        elif choice == "5":
            test_project()
        elif choice == "6":
            print_banner()
            print("\nДополнительная информация:")
            print("- Проект создан для учебных целей")
            print("- Использует ООП подход")
            print("- Поддерживает PostgreSQL и ClickHouse")
            print("- Имеет модульную структуру")
            print("\nСтруктура проекта:")
            print("  models/      - Классы данных")
            print("  parsers/     - Парсеры файлов и сайтов")
            print("  database/    - Работа с БД")
            print("  web/         - Веб-интерфейс (в разработке)")
            print("  parsed_decisions/ - Папка с данными для парсинга")
        elif choice == "0":
            print("\nВыход из программы...")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
    
    print("\nСпасибо за использование парсера судебных решений!")
    print("Для запуска тестов используйте: python run_tests.py")


if __name__ == "__main__":
    # Проверяем наличие необходимых модулей
    try:
        from parsers.text_parser import TextFileParser
        from models.document import CourtDecision
        print("Основные модули загружены успешно.")
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Установите зависимости: pip install -r requirements_parser.txt")
        sys.exit(1)
    
    # Запускаем основную программу
    main()