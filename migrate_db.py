#!/usr/bin/env python3
"""
Миграция БД на новую схему (дедупликация по URL вместо ad_id)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.db_manager import DatabaseManager
import shutil
from datetime import datetime

DB_PATH = "data/avito_ads.db"
BACKUP_PATH = f"data/avito_ads_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

print("=" * 80)
print("МИГРАЦИЯ БАЗЫ ДАННЫХ")
print("=" * 80)

# Проверяем существует ли БД
db_file = Path(DB_PATH)
if db_file.exists():
    print(f"\n✓ Найдена существующая БД: {DB_PATH}")

    # Создаём бэкап
    print(f"✓ Создаём резервную копию: {BACKUP_PATH}")
    shutil.copy(DB_PATH, BACKUP_PATH)

    # Загружаем старые данные
    print("✓ Загружаем данные из старой БД...")
    old_db = DatabaseManager(db_path=DB_PATH)
    old_ads = old_db.get_all_advertisements()
    print(f"  Найдено {len(old_ads)} объявлений")

    # Конвертируем в словари
    old_data = old_db.export_to_dict(old_ads)

    # Удаляем старую БД
    print("✓ Удаляем старую БД...")
    db_file.unlink()

    # Создаём новую БД с обновлённой схемой
    print("✓ Создаём новую БД с исправленной схемой...")
    new_db = DatabaseManager(db_path=DB_PATH)

    # Мигрируем данные (дедупликация по URL автоматически сработает)
    print("✓ Мигрируем данные (с автоматической дедупликацией по URL)...")
    stats = new_db.save_advertisements_batch(old_data)

    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТ МИГРАЦИИ:")
    print("=" * 80)
    print(f"Было объявлений: {len(old_ads)}")
    print(f"Создано уникальных: {stats['created']}")
    print(f"Обновлено: {stats['updated']}")
    print(f"Ошибок: {stats['failed']}")
    print(f"Дубликатов удалено: {len(old_ads) - stats['created']}")

    # Проверяем результат
    new_ads = new_db.get_all_advertisements()
    print(f"\nИтого в новой БД: {len(new_ads)} уникальных объявлений")
    print(f"Резервная копия сохранена: {BACKUP_PATH}")

else:
    print(f"\n✓ БД не существует, создаём новую: {DB_PATH}")
    new_db = DatabaseManager(db_path=DB_PATH)
    print("✓ БД создана с правильной схемой (дедупликация по URL)")

print("\n" + "=" * 80)
print("✓ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
print("=" * 80)
print("\nТеперь дубликаты определяются по URL, а не по динамическому ad_id")
print("Можете запускать парсинг: python main.py --query 'видеокарта' --limit 10")
