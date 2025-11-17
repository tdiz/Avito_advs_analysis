#!/usr/bin/env python3
"""
Диагностический тест: парсим реальные объявления 2 раза и смотрим что меняется
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.parsers.avito_parser import AvitoParser
from src.database.db_manager import DatabaseManager
import time

print("=" * 80)
print("ДИАГНОСТИКА: Что меняется в ad_id и URL при повторном парсинге?")
print("=" * 80)

QUERY = "видеокарта"
LOCATION = "moskva"
LIMIT = 3  # Только 3 объявления для быстроты

# Создаём тестовую БД
db = DatabaseManager(db_path="data/diagnostic.db")

print(f"\n[ПАРСИНГ №1] Парсим {LIMIT} объявлений...")
with AvitoParser(headless=True) as avito:
    batch1 = avito.search_ads(query=QUERY, location=LOCATION, max_pages=1, limit=LIMIT)

if not batch1:
    print("❌ Ничего не спарсилось! Проверьте подключение к Avito.")
    sys.exit(1)

print(f"✓ Спарсено: {len(batch1)} объявлений\n")
print("=" * 80)
print("ДАННЫЕ ПЕРВОГО ПАРСИНГА:")
print("=" * 80)
for i, ad in enumerate(batch1, 1):
    print(f"\n[{i}] {ad['title'][:60]}")
    print(f"    ad_id: {ad['id']}")
    print(f"    URL:   {ad['url']}")

# Сохраняем в БД
stats1 = db.save_advertisements_batch(batch1)
print(f"\n✓ Сохранено в БД: создано {stats1['created']}, обновлено {stats1['updated']}")

# ПАУЗА между запросами
print("\n[ПАУЗА] Ждём 10 секунд перед повторным парсингом...")
time.sleep(10)

print("\n" + "=" * 80)
print(f"[ПАРСИНГ №2] Парсим ТЕ ЖЕ {LIMIT} объявления снова...")
print("=" * 80)

with AvitoParser(headless=True) as avito:
    batch2 = avito.search_ads(query=QUERY, location=LOCATION, max_pages=1, limit=LIMIT)

if not batch2:
    print("❌ Второй парсинг failed!")
    sys.exit(1)

print(f"✓ Спарсено: {len(batch2)} объявлений\n")
print("=" * 80)
print("ДАННЫЕ ВТОРОГО ПАРСИНГА:")
print("=" * 80)
for i, ad in enumerate(batch2, 1):
    print(f"\n[{i}] {ad['title'][:60]}")
    print(f"    ad_id: {ad['id']}")
    print(f"    URL:   {ad['url']}")

# Сохраняем в БД
stats2 = db.save_advertisements_batch(batch2)
print(f"\n✓ Сохранено в БД: создано {stats2['created']}, обновлено {stats2['updated']}")

# АНАЛИЗ РАЗЛИЧИЙ
print("\n" + "=" * 80)
print("АНАЛИЗ: Что изменилось между парсингами?")
print("=" * 80)

for i in range(min(len(batch1), len(batch2))):
    ad1 = batch1[i]
    ad2 = batch2[i]

    print(f"\n[Объявление {i+1}]")
    print(f"Заголовок одинаковый: {'✓' if ad1['title'] == ad2['title'] else '✗'}")

    if ad1['id'] == ad2['id']:
        print(f"ad_id одинаковый:     ✓ ({ad1['id']})")
    else:
        print(f"ad_id РАЗНЫЕ:         ✗")
        print(f"  Парсинг 1: {ad1['id']}")
        print(f"  Парсинг 2: {ad2['id']}")

    if ad1['url'] == ad2['url']:
        print(f"URL одинаковый:       ✓")
    else:
        print(f"URL РАЗНЫЕ:           ✗")
        print(f"  Парсинг 1: {ad1['url']}")
        print(f"  Парсинг 2: {ad2['url']}")

print("\n" + "=" * 80)
print("ИТОГ:")
print("=" * 80)
print(f"Первый парсинг:  создано {stats1['created']}, обновлено {stats1['updated']}")
print(f"Второй парсинг:  создано {stats2['created']}, обновлено {stats2['updated']}")
print(f"\nОбъявлений в БД: {len(db.get_all_advertisements())}")

if stats2['updated'] == len(batch2) and stats2['created'] == 0:
    print("\n✓ ДЕДУПЛИКАЦИЯ РАБОТАЕТ! Все объявления распознаны как существующие.")
elif stats2['created'] > 0:
    print(f"\n✗ ПРОБЛЕМА! Созданы дубликаты: {stats2['created']}")
    print("Это значит что уникальный идентификатор (URL) меняется между парсингами.")
