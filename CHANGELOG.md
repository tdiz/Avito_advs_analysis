# Changelog - Avito Ads Bot

## 2025-11-17 - КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Дедупликация по URL

### Проблема
**Обнаружена критическая проблема с дубликатами объявлений в БД:**

1. Avito генерирует **динамические `ad_id`** при каждом запросе
2. Один и тот же товар получает РАЗНЫЕ `ad_id` в разных сессиях
3. UNIQUE constraint на `ad_id` не работал - создавались дубликаты
4. При парсинге 10 объявлений логи показывали "Создано: 1, обновлено: 9", но реально в БД сохранялись только некоторые из-за конфликтов

**Пример:**
```
MSI GeForce RTX 3090 - ad_id: YToyOntzOjEzOiJsb2NhbFByaW9yaX... (01:19)
MSI GeForce RTX 3090 - ad_id: YToyOntzOjEzOiJsb2NhbFByaW9yaX... (00:59)
```
Один товар, два разных ID!

### Решение
**Переключились на дедупликацию по URL (стабильный идентификатор):**

#### Изменения в `src/database/models.py` (строки 21-24):
```python
# БЫЛО:
ad_id = Column(String(50), unique=True, index=True, nullable=False)
url = Column(Text, nullable=False)

# СТАЛО:
ad_id = Column(String(255), nullable=True, index=True)  # Может быть динамическим
url = Column(String(1000), unique=True, nullable=False, index=True)  # URL - стабильный идентификатор
```

#### Изменения в `src/database/db_manager.py` (строки 59-62):
```python
# БЫЛО: Проверка по ad_id
existing_ad = session.query(Advertisement).filter_by(
    ad_id=ad_data.get("id")
).first()

# СТАЛО: Проверка по URL
existing_ad = session.query(Advertisement).filter_by(
    url=ad_data.get("url")
).first()
```

### Результат
✅ **Дубликаты больше не создаются**
✅ **Повторный парсинг обновляет существующие объявления**
✅ **Честная статистика: "Создано: 10" / "Обновлено: 10"**

**Тест:**
- Первый парсинг 10 объявлений: создано 10 ✓
- Второй парсинг (те же, но новые ad_id): создано 0, обновлено 10 ✓
- В БД: 10 уникальных объявлений (было бы 20 без исправления)

### Миграция существующих данных
```bash
python migrate_db.py  # Автоматически удаляет дубликаты из старой БД
```

### Тесты
- `test_deduplication.py` - демонстрация проблемы с динамическими ad_id
- `test_url_dedup.py` - проверка работы исправления
- `inspect_db.py` - детальная инспекция БД с полными ad_id

---

## Другие улучшения в этой сессии

### Честная статистика сохранения (main.py, db_manager.py)
**БЫЛО:** "Сохранено: 10" (неясно, созданы или обновлены)
**СТАЛО:** "Создано: 1, обновлено: 9, ошибок: 0" (детальная статистика)

### Вывод URL при старте парсинга (main.py:310-313)
```python
base_url = "https://www.avito.ru"
search_url = f"{base_url}/{args.location}?q={args.query}&p=1"
logger.info(f"URL для проверки: {search_url}")
```

### Параметр --limit для контроля количества
```bash
python main.py --query "видеокарта" --limit 10  # Только первые 10
```

### Исправление DateTime ошибки (avito_parser.py:221)
**БЫЛО:** `"parsed_at": datetime.now().isoformat()` (строка → ошибка)
**СТАЛО:** `"parsed_at": datetime.now()` (datetime объект ✓)

---

## Технические детали

### Почему ad_id от Avito динамический?
`ad_id` похоже кодирует сессионные данные (Base64):
```
YToyOntzOjEzOiJsb2NhbFByaW9yaX...
```

Это может быть:
- Session token
- Timestamp
- Location priority
- Search context

**Вывод:** ad_id НЕ является стабильным идентификатором объявления!

### Почему URL надёжнее?
URL содержит уникальный ID объявления в пути:
```
https://www.avito.ru/moskva/tovary_dlya_kompyutera/videokarty-1234567890
                                                                  ^^^^^^^^^^
                                                              стабильный ID
```

Этот ID НЕ меняется и уникально идентифицирует объявление.
