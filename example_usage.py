#!/usr/bin/env python3
"""
Примеры использования модулей бота для анализа Avito
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.parsers.avito_parser import AvitoParser
from src.database.db_manager import DatabaseManager
from src.analytics.analyzer import AvitoAnalyzer
from src.utils.logger import setup_logger


def example_basic_parsing():
    """Пример базового парсинга"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 1: Базовый парсинг")
    print("=" * 60)

    logger = setup_logger()

    with AvitoParser(headless=True) as parser:
        ads = parser.search_ads(
            query="ноутбук",
            location="moskva",
            max_pages=1
        )

        print(f"\nНайдено {len(ads)} объявлений")
        if ads:
            print("\nПример объявления:")
            print(f"Заголовок: {ads[0].get('title')}")
            print(f"Цена: {ads[0].get('price')} ₽")
            print(f"Адрес: {ads[0].get('address')}")


def example_with_database():
    """Пример с сохранением в базу данных"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 2: Парсинг с сохранением в БД")
    print("=" * 60)

    logger = setup_logger()

    # Инициализация БД
    db = DatabaseManager(db_path="data/example_ads.db")

    # Парсинг
    with AvitoParser(headless=True) as parser:
        ads = parser.search_ads(
            query="iPhone",
            location="moskva",
            max_pages=1
        )

        # Сохранение
        saved = db.save_advertisements_batch(ads)
        print(f"\nСохранено {saved} объявлений в базу данных")

        # Получение статистики
        stats = db.get_statistics()
        print("\nСтатистика БД:")
        print(f"Всего объявлений: {stats['total_advertisements']}")
        print(f"Средняя цена: {stats['average_price']:.2f} ₽")


def example_with_analysis():
    """Пример с анализом данных"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 3: Парсинг с анализом")
    print("=" * 60)

    logger = setup_logger()

    # Парсинг
    with AvitoParser(headless=True) as parser:
        ads = parser.search_ads(
            query="MacBook",
            location="moskva",
            max_pages=2
        )

        # Анализ
        analyzer = AvitoAnalyzer()

        # Анализ цен
        price_stats = analyzer.analyze_prices(ads)
        print("\nАнализ цен:")
        print(f"Средняя цена: {price_stats['mean']:.2f} ₽")
        print(f"Медиана: {price_stats['median']:.2f} ₽")
        print(f"Мин: {price_stats['min']:.2f} ₽")
        print(f"Макс: {price_stats['max']:.2f} ₽")

        # Ключевые слова
        keywords = analyzer.analyze_keywords(ads, top_n=10)
        print("\nТоп-10 ключевых слов:")
        for kw in keywords['top_keywords']:
            print(f"  {kw['keyword']}: {kw['frequency']}")


def example_export_data():
    """Пример экспорта данных"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 4: Экспорт данных")
    print("=" * 60)

    logger = setup_logger()

    # Парсинг
    with AvitoParser(headless=True) as parser:
        ads = parser.search_ads(
            query="смартфон",
            location="moskva",
            max_pages=1
        )

        # Экспорт
        analyzer = AvitoAnalyzer()

        # В CSV
        analyzer.export_to_csv(ads, "data/smartphones.csv")
        print("\nДанные экспортированы в data/smartphones.csv")

        # В JSON
        analyzer.export_to_json(ads, "data/smartphones.json")
        print("Данные экспортированы в data/smartphones.json")

        # Генерация отчета
        report = analyzer.generate_report(ads)
        analyzer.save_report(report, "data/report.json")
        print("Отчет сохранен в data/report.json")


def example_search_in_database():
    """Пример поиска в базе данных"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 5: Поиск в базе данных")
    print("=" * 60)

    db = DatabaseManager(db_path="data/avito_ads.db")

    # Поиск по критериям
    results = db.search_advertisements(
        query="ноутбук",
        min_price=30000,
        max_price=100000
    )

    print(f"\nНайдено {len(results)} объявлений")
    print("Критерии: запрос='ноутбук', цена от 30000 до 100000 ₽")

    if results:
        for ad in results[:5]:  # Первые 5
            print(f"\n- {ad.title}")
            print(f"  Цена: {ad.price} ₽")
            print(f"  URL: {ad.url}")


def example_detailed_info():
    """Пример получения детальной информации об объявлении"""
    print("\n" + "=" * 60)
    print("ПРИМЕР 6: Детальная информация")
    print("=" * 60)

    logger = setup_logger()

    with AvitoParser(headless=True) as parser:
        # Сначала ищем объявления
        ads = parser.search_ads(
            query="MacBook Pro",
            location="moskva",
            max_pages=1
        )

        if ads:
            # Получаем детали первого объявления
            first_ad = ads[0]
            print(f"\nПолучаем детали для: {first_ad['title']}")

            details = parser.get_ad_details(first_ad['url'])

            if details:
                print(f"\nПолное описание: {details.get('full_description', 'N/A')[:200]}...")
                print(f"Количество изображений: {len(details.get('images', []))}")
                print(f"Просмотров: {details.get('views', 'N/A')}")

                if details.get('characteristics'):
                    print("\nХарактеристики:")
                    for key, value in list(details['characteristics'].items())[:5]:
                        print(f"  {key}: {value}")


def main():
    """Запуск примеров"""
    print("\n" + "=" * 60)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ БОТА AVITO ADS ANALYSIS")
    print("=" * 60)

    # Раскомментируйте нужный пример:

    # example_basic_parsing()
    # example_with_database()
    # example_with_analysis()
    # example_export_data()
    # example_search_in_database()
    # example_detailed_info()

    print("\n" + "=" * 60)
    print("Раскомментируйте нужную функцию в main() для запуска примера")
    print("=" * 60)


if __name__ == "__main__":
    main()
