#!/usr/bin/env python3
"""
Детальная инспекция БД - показываем ВСЕ поля включая полные ad_id
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db_manager import DatabaseManager

print("=" * 80)
print("ДЕТАЛЬНАЯ ИНСПЕКЦИЯ БАЗЫ ДАННЫХ")
print("=" * 80)

db = DatabaseManager(db_path="data/avito_ads.db")

# Получаем ВСЕ объявления
all_ads = db.get_all_advertisements()

print(f"\nВсего объявлений в БД: {len(all_ads)}")
print("=" * 80)

for i, ad in enumerate(all_ads, 1):
    print(f"\n[{i}] ОБЪЯВЛЕНИЕ:")
    print(f"    AD_ID (полный):  {ad.ad_id}")
    print(f"    Заголовок:       {ad.title}")
    print(f"    Цена:            {ad.price} ₽")
    print(f"    Адрес:           {ad.address}")
    print(f"    URL:             {ad.url}")
    print(f"    Спарсено:        {ad.parsed_at}")
    print(f"    Обновлено:       {ad.updated_at}")
    print(f"    Активно:         {ad.is_active}")

print("\n" + "=" * 80)
print("АНАЛИЗ ДУБЛИКАТОВ ПО ЗАГОЛОВКАМ:")
print("=" * 80)

# Группируем по заголовкам
from collections import defaultdict
titles_map = defaultdict(list)
for ad in all_ads:
    titles_map[ad.title].append(ad)

for title, ads_list in titles_map.items():
    if len(ads_list) > 1:
        print(f"\n❌ ДУБЛИКАТ: '{title}' ({len(ads_list)} раз)")
        for ad in ads_list:
            print(f"   - ad_id: {ad.ad_id}")
            print(f"     спарсено: {ad.parsed_at}")
