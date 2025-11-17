#!/usr/bin/env python3
"""
Базовый тест функциональности бота (без реального парсинга)
"""
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("ТЕСТИРОВАНИЕ КОМПОНЕНТОВ AVITO BOT")
print("=" * 60)

# Тест 1: Импорты
print("\n[1/5] Проверка импортов...")
try:
    from src.database.db_manager import DatabaseManager
    from src.analytics.analyzer import AvitoAnalyzer
    from src.utils.logger import setup_logger
    print("✓ Все модули импортируются корректно")
except Exception as e:
    print(f"✗ Ошибка импорта: {e}")
    sys.exit(1)

# Тест 2: Инициализация БД
print("\n[2/5] Проверка инициализации БД...")
try:
    db = DatabaseManager(db_path="data/test_db.db")
    print("✓ База данных инициализирована")
    print(f"  Путь: {db.db_path}")
except Exception as e:
    print(f"✗ Ошибка БД: {e}")
    sys.exit(1)

# Тест 3: Сохранение тестовых данных
print("\n[3/5] Проверка сохранения данных...")
try:
    test_ads = [
        {
            "id": "test_001",
            "title": "Тестовый ноутбук MacBook Pro",
            "price": 150000,
            "url": "https://avito.ru/test/001",
            "description": "Тестовое описание",
            "address": "Москва, Центральный район",
            "published_date": "Сегодня",
            "seller": "Тестовый продавец"
        },
        {
            "id": "test_002",
            "title": "Тестовый iPhone 15 Pro",
            "price": 120000,
            "url": "https://avito.ru/test/002",
            "description": "Еще одно тестовое описание",
            "address": "Москва, Северный район",
            "published_date": "Вчера",
            "seller": "Другой продавец"
        },
        {
            "id": "test_003",
            "title": "Тестовый ноутбук Lenovo ThinkPad",
            "price": 85000,
            "url": "https://avito.ru/test/003",
            "description": "Третье тестовое объявление",
            "address": "Санкт-Петербург",
            "published_date": "2 дня назад",
            "seller": "Тестовый продавец"
        }
    ]

    saved = db.save_advertisements_batch(test_ads)
    print(f"✓ Сохранено {saved} тестовых объявлений")
except Exception as e:
    print(f"✗ Ошибка при сохранении: {e}")
    sys.exit(1)

# Тест 4: Чтение из БД
print("\n[4/5] Проверка чтения из БД...")
try:
    # Поиск по запросу
    results = db.search_advertisements(query="ноутбук")
    print(f"✓ Найдено {len(results)} объявлений по запросу 'ноутбук'")

    # Фильтрация по цене
    expensive = db.search_advertisements(query="", min_price=100000)
    print(f"✓ Найдено {len(expensive)} объявлений дороже 100000 ₽")

    # Получение статистики
    stats = db.get_statistics()
    print(f"✓ Статистика БД:")
    print(f"  - Всего объявлений: {stats['total_advertisements']}")
    print(f"  - Средняя цена: {stats['average_price']:.2f} ₽")
except Exception as e:
    print(f"✗ Ошибка при чтении: {e}")
    sys.exit(1)

# Тест 5: Анализ данных
print("\n[5/5] Проверка модуля анализа...")
try:
    analyzer = AvitoAnalyzer()

    # Конвертируем объекты в словари
    ads_dicts = db.export_to_dict(db.get_all_advertisements())

    # Анализ цен
    price_stats = analyzer.analyze_prices(ads_dicts)
    print(f"✓ Анализ цен выполнен:")
    print(f"  - Количество: {price_stats['count']}")
    print(f"  - Средняя цена: {price_stats['mean']:.2f} ₽")
    print(f"  - Медиана: {price_stats['median']:.2f} ₽")
    print(f"  - Диапазон: {price_stats['min']:.2f} - {price_stats['max']:.2f} ₽")

    # Анализ ключевых слов
    keywords = analyzer.analyze_keywords(ads_dicts)
    print(f"✓ Анализ ключевых слов:")
    for kw in keywords['top_keywords'][:5]:
        print(f"  - {kw['keyword']}: {kw['frequency']}")

    # Экспорт в JSON
    analyzer.export_to_json(ads_dicts, "data/test_export.json")
    print(f"✓ Экспорт в JSON выполнен")

except Exception as e:
    print(f"✗ Ошибка при анализе: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
print("=" * 60)
print("\nБот готов к работе. Основные компоненты функционируют корректно.")
print("\nСледующий шаг: Установите зависимости для парсинга:")
print("  pip install -r requirements.txt")
print("\nЗатем можете запустить реальный парсинг:")
print("  python run.py --query 'ноутбук' --location 'moskva' --pages 1")
