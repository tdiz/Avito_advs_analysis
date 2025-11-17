#!/usr/bin/env python3
"""
Главный модуль бота для анализа объявлений Avito

Пример использования:
    # Парсинг и анализ
    python main.py --query "ноутбук" --location "moskva" --pages 3 --analyze

    # Только анализ данных из БД (без парсинга)
    python main.py --query "ноутбук" --from-db --analyze

    # Парсинг и экспорт
    python main.py --query "iPhone" --location "moskva" --export-csv data/iphones.csv
"""
import argparse
import sys
from pathlib import Path

from src.parsers.avito_parser import AvitoParser
from src.database.db_manager import DatabaseManager
from src.analytics.analyzer import AvitoAnalyzer
from src.utils.logger import setup_logger


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Бот для исследования объявлений на Avito'
    )
    parser.add_argument(
        '--query',
        type=str,
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
        help='Выполнить анализ данных'
    )
    parser.add_argument(
        '--from-db',
        action='store_true',
        help='Использовать данные из БД (без парсинга)'
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
    parser.add_argument(
        '--min-price',
        type=float,
        help='Минимальная цена для фильтрации из БД'
    )
    parser.add_argument(
        '--max-price',
        type=float,
        help='Максимальная цена для фильтрации из БД'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Максимальное количество объявлений для парсинга (например, 10)'
    )

    return parser.parse_args()


def fetch_ads_from_parser(args, logger):
    """
    Парсинг объявлений с Avito

    Returns:
        List[Dict]: Список объявлений
    """
    logger.info("Начинаем парсинг объявлений...")

    try:
        with AvitoParser(headless=args.headless) as avito:
            ads = avito.search_ads(
                query=args.query,
                location=args.location,
                max_pages=args.pages,
                limit=args.limit
            )

            if not ads:
                logger.warning("Объявления не найдены")
                return []

            logger.info(f"Найдено {len(ads)} объявлений")
            return ads

    except ConnectionError as e:
        logger.error(f"Ошибка подключения к Avito: {e}")
        return []
    except TimeoutError as e:
        logger.error(f"Таймаут при парсинге: {e}")
        return []
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при парсинге: {e}", exc_info=True)
        return []


def fetch_ads_from_db(db, args, logger):
    """
    Получение объявлений из базы данных

    Returns:
        List[Dict]: Список объявлений в формате словарей
    """
    logger.info("Получение данных из базы данных...")

    try:
        ads_objects = db.search_advertisements(
            query=args.query,
            min_price=args.min_price,
            max_price=args.max_price
        )

        if not ads_objects:
            logger.warning(f"Объявления по запросу '{args.query}' не найдены в БД")
            return []

        # Конвертируем объекты Advertisement в словари
        ads = db.export_to_dict(ads_objects)
        logger.info(f"Загружено {len(ads)} объявлений из БД")
        return ads

    except Exception as e:
        logger.error(f"Ошибка при чтении из БД: {e}", exc_info=True)
        return []


def save_ads_to_db(db, ads, args, logger):
    """Сохранение объявлений в базу данных"""
    if not ads:
        return {'created': 0, 'updated': 0, 'failed': 0}

    logger.info("Сохранение объявлений в базу данных...")

    try:
        stats = db.save_advertisements_batch(ads)
        logger.info(f"Создано: {stats['created']}, обновлено: {stats['updated']}, ошибок: {stats['failed']}")

        # Сохранение поискового запроса
        db.save_search_query(args.query, args.location, len(ads))

        return stats

    except Exception as e:
        logger.error(f"Ошибка при сохранении в БД: {e}", exc_info=True)
        return {'created': 0, 'updated': 0, 'failed': 0}


def perform_analysis(ads, args, logger):
    """Выполнение анализа данных"""
    if not ads:
        logger.warning("Нет данных для анализа")
        return

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
    if price_stats['count'] > 0:
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
        try:
            analyzer.save_report(report, args.report)
            logger.info(f"Отчет сохранен в {args.report}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении отчета: {e}")


def perform_export(ads, args, logger):
    """Экспорт данных в файлы"""
    if not ads:
        logger.warning("Нет данных для экспорта")
        return

    analyzer = AvitoAnalyzer()

    if args.export_csv:
        try:
            analyzer.export_to_csv(ads, args.export_csv)
            logger.info(f"Данные экспортированы в CSV: {args.export_csv}")
        except Exception as e:
            logger.error(f"Ошибка при экспорте CSV: {e}")

    if args.export_json:
        try:
            analyzer.export_to_json(ads, args.export_json)
            logger.info(f"Данные экспортированы в JSON: {args.export_json}")
        except Exception as e:
            logger.error(f"Ошибка при экспорте JSON: {e}")


def print_db_stats(db, logger):
    """Вывод статистики базы данных"""
    try:
        stats = db.get_statistics()
        print("\n" + "=" * 60)
        print("СТАТИСТИКА БАЗЫ ДАННЫХ")
        print("=" * 60)
        print(f"Всего объявлений: {stats['total_advertisements']}")
        print(f"Активных объявлений: {stats['active_advertisements']}")
        print(f"Поисковых запросов: {stats['total_search_queries']}")
        if stats['average_price'] > 0:
            print(f"Средняя цена в БД: {stats['average_price']:.2f} ₽")
    except Exception as e:
        logger.error(f"Ошибка при получении статистики БД: {e}")


def main():
    """Главная функция бота"""
    args = parse_arguments()

    # Настройка логгера
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info("Запуск бота для анализа объявлений Avito")
    logger.info("=" * 60)

    # Валидация аргументов
    if not args.from_db and not args.query:
        logger.error("Требуется указать --query для парсинга или --from-db для работы с БД")
        sys.exit(1)

    # Инициализация базы данных
    try:
        db = DatabaseManager(db_path=args.db_path)
        logger.info(f"База данных: {args.db_path}")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}", exc_info=True)
        sys.exit(1)

    try:
        # Получение данных (из парсера или из БД)
        if args.from_db:
            logger.info("Режим работы: чтение из базы данных")
            ads = fetch_ads_from_db(db, args, logger)
        else:
            logger.info("Режим работы: парсинг объявлений")
            logger.info(f"Поисковый запрос: '{args.query}'")
            logger.info(f"Локация: {args.location}")
            logger.info(f"Количество страниц: {args.pages}")

            ads = fetch_ads_from_parser(args, logger)

            # Сохранение в БД
            if ads:
                save_ads_to_db(db, ads, args, logger)

        # Анализ данных (если требуется)
        if args.analyze:
            perform_analysis(ads, args, logger)

        # Экспорт данных (если требуется)
        if args.export_csv or args.export_json:
            perform_export(ads, args, logger)

        # Статистика БД
        print_db_stats(db, logger)

        logger.info("=" * 60)
        logger.info("Работа бота завершена успешно")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.warning("Работа бота прервана пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
