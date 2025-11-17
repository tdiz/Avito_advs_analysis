#!/usr/bin/env python3
"""
Быстрая проверка содержимого БД
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db_manager import DatabaseManager

print("=" * 60)
print("ПРОВЕРКА БАЗЫ ДАННЫХ")
print("=" * 60)

# Проверяем основную БД
db = DatabaseManager(db_path="data/avito_ads.db")

# Статистика
stats = db.get_statistics()
print(f"\nВсего объявлений: {stats['total_advertisements']}")
print(f"Активных: {stats['active_advertisements']}")
if stats['average_price'] > 0:
    print(f"Средняя цена: {stats['average_price']:.2f} ₽")

# Показываем последние 10 объявлений
print("\n" + "=" * 60)
print("ПОСЛЕДНИЕ 10 ОБЪЯВЛЕНИЙ:")
print("=" * 60)

all_ads = db.get_all_advertisements()
if all_ads:
    for ad in all_ads[:10]:
        print(f"\n{ad.title}")
        print(f"  Цена: {ad.price} ₽")
        print(f"  Адрес: {ad.address}")
        print(f"  Дата парсинга: {ad.parsed_at}")
else:
    print("\nБаза данных пустая!")

print("\n" + "=" * 60)
