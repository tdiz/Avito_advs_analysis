#!/usr/bin/env python3
"""
Тест дедупликации - имитируем ситуацию с динамическими ad_id от Avito
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db_manager import DatabaseManager

print("=" * 80)
print("ТЕСТ ДЕДУПЛИКАЦИИ С ДИНАМИЧЕСКИМИ AD_ID")
print("=" * 80)

# Создаём тестовую БД
db = DatabaseManager(db_path="data/test_dedup.db")

# СЦЕНАРИЙ: Парсим 10 объявлений, среди них есть дубликаты по содержанию,
# но с РАЗНЫМИ ad_id (как Avito генерирует динамические ID)

print("\n[ПЕРВЫЙ ПАРСИНГ] Сохраняем 10 объявлений...")
first_batch = []
for i in range(10):
    ad = {
        "id": f"dynamic_id_batch1_{i}",  # Первый набор ID
        "title": f"Товар номер {i % 5}",  # Только 5 уникальных товаров
        "price": (i % 5 + 1) * 10000,
        "url": f"https://avito.ru/item_{i}",
        "description": f"Описание товара {i % 5}",
        "address": "Москва",
        "published_date": "Сегодня",
        "seller": f"Продавец {i % 3}"  # Только 3 продавца
    }
    first_batch.append(ad)

stats1 = db.save_advertisements_batch(first_batch)
print(f"Результат: Создано: {stats1['created']}, обновлено: {stats1['updated']}, ошибок: {stats1['failed']}")

# Проверяем что в БД
ads_in_db = db.get_all_advertisements()
print(f"Объявлений в БД после первого парсинга: {len(ads_in_db)}")

print("\n" + "=" * 80)
print("[ВТОРОЙ ПАРСИНГ] Парсим те же объявления, но Avito выдал НОВЫЕ ad_id...")
second_batch = []
for i in range(10):
    ad = {
        "id": f"dynamic_id_batch2_{i}",  # НОВЫЕ ID, но тот же контент!
        "title": f"Товар номер {i % 5}",  # Те же заголовки
        "price": (i % 5 + 1) * 10000,  # Те же цены
        "url": f"https://avito.ru/item_{i}",  # Те же URL
        "description": f"Описание товара {i % 5}",
        "address": "Москва",
        "published_date": "Сегодня",
        "seller": f"Продавец {i % 3}"
    }
    second_batch.append(ad)

stats2 = db.save_advertisements_batch(second_batch)
print(f"Результат: Создано: {stats2['created']}, обновлено: {stats2['updated']}, ошибок: {stats2['failed']}")

# Проверяем что в БД
ads_in_db = db.get_all_advertisements()
print(f"Объявлений в БД после второго парсинга: {len(ads_in_db)}")

print("\n" + "=" * 80)
print("ДЕТАЛИ ОБЪЯВЛЕНИЙ В БД:")
print("=" * 80)

from collections import defaultdict
by_title = defaultdict(list)

for ad in ads_in_db:
    by_title[ad.title].append(ad)

for title, ads_list in sorted(by_title.items()):
    print(f"\n'{title}' - найдено {len(ads_list)} раз:")
    for ad in ads_list:
        print(f"  - ad_id: {ad.ad_id}")
        print(f"    цена: {ad.price}, спарсено: {ad.parsed_at}")

print("\n" + "=" * 80)
print("ПРОБЛЕМА:")
print("=" * 80)
print(f"Ожидали: 5 уникальных товаров (по содержанию)")
print(f"Получили: {len(ads_in_db)} записей в БД")
print(f"\nЕсли ad_id динамические, то UNIQUE constraint на ad_id НЕ РАБОТАЕТ!")
print("Каждый парсинг будет создавать дубликаты.")
