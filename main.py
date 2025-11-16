#!/usr/bin/env python3
"""
Главный модуль бота для анализа объявлений Avito

Пример использования:
    python main.py --query "ноутбук" --location "moskva" --pages 3
"""
import argparse
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from src.parsers.avito_parser import AvitoParser
from src.database.db_manager import DatabaseManager
from src.analytics.analyzer import AvitoAnalyzer
from src.utils.logger import setup_logger


def main():
    """Главная функция бота"""

    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(
        description='Бот для исследования объявлений на Avito'
    )
    parser.add_argument(
        '--query',
        type=str,
        required=True,
        help='Поисковый запрос (например, "ноутбук")'
    )
    parser.add_argument(
        '--location',
        type=str,
        default='rossiya',
        help='Локация для поиска (например, "moskva", "sankt-peterburg", "rossiya")'
    )
    parser.add_argument(
        '--pages',
        type=int,
        default=1,
        help='Количество страниц для парсинга (по умолчанию 1)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Запустить браузер в headless режиме'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Выполнить анализ собранных данных'
    )
    parser.add_argument(
        '--export-csv',
        type=str,
        help='Экспортировать результаты в CSV файл'
    )
    parser.add_argument(
        '--export-json',
        type=str,
        help='Экспортировать результаты в JSON файл'
    )
    parser.add_argument(
        '--report',
        type=str,
        help='Сохранить отчет в файл'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default='data/avito_ads.db',
        help='Путь к базе данных (по умолчанию data/avito_ads.db)'
    )

    args = parser.parse_args()

    # Настройка логгера
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info("Запуск бота для анализа объявлений Avito")
    logger.info("=" * 60)

    # Инициализация базы данных
    db = DatabaseManager(db_path=args.db_path)
    logger.info(f"База данных: {args.db_path}")

    # Инициализация парсера
    logger.info(f"Поисковый запрос: '{args.query}'")
    logger.info(f"Локация: {args.location}")
    logger.info(f"Количество страниц: {args.pages}")

    try:
        with AvitoParser(headless=args.headless) as avito:
            # Парсинг объявлений
            logger.info("Начинаем парсинг объявлений...")
            ads = avito.search_ads(
                query=args.query,
                location=args.location,
                max_pages=args.pages
            )

            if not ads:
                logger.warning("Объявления не найдены")
                return

            logger.info(f"Найдено {len(ads)} объявлений")

            # Сохранение в базу данных
            logger.info("Сохранение объявлений в базу данных...")
            saved_count = db.save_advertisements_batch(ads)
            logger.info(f"Сохранено {saved_count} объявлений")

            # Сохранение поискового запроса
            db.save_search_query(args.query, args.location, len(ads))

            # Анализ данных
            if args.analyze:
                logger.info("=" * 60)
                logger.info("Анализ данных")
                logger.info("=" * 60)

                analyzer = AvitoAnalyzer()

                # Генерация отчета
                report = analyzer.generate_report(ads)

                # Вывод основной статистики
                print("\n" + "=" * 60)
                print("СТАТИСТИКА ПО ЦЕНАМ")
                print("=" * 60)
                price_stats = report['price_analysis']
                print(f"Количество объявлений с ценой: {price_stats['count']}")
                print(f"Средняя цена: {price_stats['mean']:.2f} ₽")
                print(f"Медианная цена: {price_stats['median']:.2f} ₽")
                print(f"Минимальная цена: {price_stats['min']:.2f} ₽")
                print(f"Максимальная цена: {price_stats['max']:.2f} ₽")

                print("\n" + "=" * 60)
                print("ТОП-10 КЛЮЧЕВЫХ СЛОВ")
                print("=" * 60)
                for keyword in report['keyword_analysis']['top_keywords']:
                    print(f"{keyword['keyword']}: {keyword['frequency']}")

                print("\n" + "=" * 60)
                print("ТОП-10 ЛОКАЦИЙ")
                print("=" * 60)
                for loc in report['location_analysis']['top_locations']:
                    print(f"{loc['location']}: {loc['count']} объявлений")

                # Сохранение отчета
                if args.report:
                    analyzer.save_report(report, args.report)
                    logger.info(f"Отчет сохранен в {args.report}")

            # Экспорт данных
            if args.export_csv or args.export_json:
                analyzer = AvitoAnalyzer()

                if args.export_csv:
                    analyzer.export_to_csv(ads, args.export_csv)
                    logger.info(f"Данные экспортированы в CSV: {args.export_csv}")

                if args.export_json:
                    analyzer.export_to_json(ads, args.export_json)
                    logger.info(f"Данные экспортированы в JSON: {args.export_json}")

            # Статистика базы данных
            stats = db.get_statistics()
            print("\n" + "=" * 60)
            print("СТАТИСТИКА БАЗЫ ДАННЫХ")
            print("=" * 60)
            print(f"Всего объявлений: {stats['total_advertisements']}")
            print(f"Активных объявлений: {stats['active_advertisements']}")
            print(f"Поисковых запросов: {stats['total_search_queries']}")
            print(f"Средняя цена в БД: {stats['average_price']:.2f} ₽")

            logger.info("=" * 60)
            logger.info("Работа бота завершена успешно")
            logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.warning("Работа бота прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Ошибка при выполнении: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
