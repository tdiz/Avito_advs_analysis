#!/usr/bin/env python3
"""
Тест дедупликации по URL (исправленная версия)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db_manager import DatabaseManager

print("=" * 80)
print("ТЕСТ ДЕДУПЛИКАЦИИ ПО URL (ИСПРАВЛЕНО)")
print("=" * 80)

# Создаём новую тестовую БД
db = DatabaseManager(db_path="data/test_url_dedup.db")

# СЦЕНАРИЙ: Парсим одни и те же объявления дважды
# Avito выдаёт РАЗНЫЕ ad_id, но URL одинаковый

print("\n[ПЕРВЫЙ ПАРСИНГ] Сохраняем 10 объявлений...")
first_batch = []
for i in range(10):
    ad = {
        "id": f"dynamic_session1_encoded_id_{i}",  # Динамический ID
        "title": f"Видеокарта RTX {4090 - i}",
        "price": (i + 1) * 15000,
        "url": f"https://www.avito.ru/moskva/tovary_dlya_kompyutera/videokarty-{1000+i}",  # СТАБИЛЬНЫЙ URL
        "description": f"Отличная видеокарта в хорошем состоянии",
        "address": "Москва, Центральный район",
        "published_date": "Сегодня",
        "seller": f"Продавец_{i % 3}"
    }
    first_batch.append(ad)

stats1 = db.save_advertisements_batch(first_batch)
print(f"✓ Создано: {stats1['created']}, обновлено: {stats1['updated']}, ошибок: {stats1['failed']}")

ads_after_first = db.get_all_advertisements()
print(f"✓ Объявлений в БД: {len(ads_after_first)}")

print("\n" + "=" * 80)
print("[ВТОРОЙ ПАРСИНГ] Парсим те же 10 объявлений, но с НОВЫМИ ad_id от Avito...")
second_batch = []
for i in range(10):
    ad = {
        "id": f"dynamic_session2_different_encoded_id_{i}",  # НОВЫЙ ID!
        "title": f"Видеокарта RTX {4090 - i}",  # Тот же заголовок
        "price": (i + 1) * 15500,  # Цена слегка изменилась (обновление)
        "url": f"https://www.avito.ru/moskva/tovary_dlya_kompyutera/videokarty-{1000+i}",  # ТОТ ЖЕ URL!
        "description": f"Отличная видеокарта в отличном состоянии",  # Описание обновлено
        "address": "Москва, Центральный район",
        "published_date": "Сегодня",
        "seller": f"Продавец_{i % 3}"
    }
    second_batch.append(ad)

stats2 = db.save_advertisements_batch(second_batch)
print(f"✓ Создано: {stats2['created']}, обновлено: {stats2['updated']}, ошибок: {stats2['failed']}")

ads_after_second = db.get_all_advertisements()
print(f"✓ Объявлений в БД: {len(ads_after_second)}")

print("\n" + "=" * 80)
print("ПРОВЕРКА РЕЗУЛЬТАТОВ:")
print("=" * 80)

if len(ads_after_second) == 10:
    print("✓ УСПЕХ! Дубликатов нет - все 10 объявлений уникальны")
    print("✓ Дедупликация по URL работает корректно!")

    # Проверяем что цены обновились
    print("\n" + "=" * 80)
    print("ПРОВЕРКА ОБНОВЛЕНИЯ ЦЕН:")
    print("=" * 80)
    for ad in ads_after_second[:3]:
        print(f"\n{ad.title}")
        print(f"  Цена: {ad.price} ₽ (должна быть обновлена)")
        print(f"  ad_id: {ad.ad_id} (может быть любой)")
        print(f"  URL: {ad.url}")
        print(f"  Описание: {ad.description}")
else:
    print(f"✗ ОШИБКА! Ожидали 10 объявлений, но в БД {len(ads_after_second)}")
    print("✗ Дедупликация не работает!")

print("\n" + "=" * 80)
print("ИТОГ:")
print("=" * 80)
print(f"Первый парсинг: создано {stats1['created']}, обновлено {stats1['updated']}")
print(f"Второй парсинг: создано {stats2['created']}, обновлено {stats2['updated']}")
print(f"Итого в БД: {len(ads_after_second)} объявлений")
print("\nТеперь дубликаты определяются по URL, а не по динамическому ad_id!")
