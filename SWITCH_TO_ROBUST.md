# Как переключиться на комбинированную дедупликацию

## Когда это нужно?

Запустите тест:
```bash
python test_real_parsing.py
```

Если результат показывает:
```
✗ ПРОБЛЕМА! Созданы дубликаты: 3
Это значит что уникальный идентификатор (URL) меняется между парсингами.
```

То URL ТОЖЕ динамические! Нужна комбинированная дедупликация.

---

## Шаги переключения

### 1. Обновите models.py

Уберите `unique=True` с URL:

```python
# Файл: src/database/models.py
# Строка 24

# БЫЛО:
url = Column(String(1000), unique=True, nullable=False, index=True)

# СТАЛО:
url = Column(String(1000), nullable=False, index=True)  # Убрали unique=True
```

### 2. Обновите main.py

Замените импорт:

```python
# Строка 20

# БЫЛО:
from src.database.db_manager import DatabaseManager

# СТАЛО:
from src.database.db_manager_robust import DatabaseManagerRobust as DatabaseManager
```

### 3. Пересоздайте БД

```bash
python migrate_db.py
```

Это пересоздаст БД с новой схемой (без UNIQUE на URL).

---

## Как работает комбинированная дедупликация?

```python
# 1. Сначала пробуем найти по URL
existing = session.query(Advertisement).filter_by(url=url).first()

# 2. Если не нашли - ищем по содержимому
if not existing:
    existing = session.query(Advertisement).filter(
        Advertisement.title == title,
        Advertisement.price == price,
        Advertisement.seller == seller,
        Advertisement.address == address
    ).first()
```

**Преимущества:**
- Работает даже если И ad_id, И URL динамические
- Обновляет объявления при изменении цены
- Не создаёт дубликаты одинаковых товаров

**Недостатки:**
- Медленнее (два запроса к БД)
- Может не распознать объявление если продавец изменил заголовок

---

## Проверка работы

После переключения запустите снова:

```bash
python test_real_parsing.py
```

Должно быть:
```
✓ ДЕДУПЛИКАЦИЯ РАБОТАЕТ! Все объявления распознаны как существующие.
Второй парсинг:  создано 0, обновлено 3
```

---

## Откат назад

Если вдруг захотите вернуться к дедупликации только по URL:

1. Верните `unique=True` в models.py строка 24
2. Верните импорт в main.py строка 20:
   ```python
   from src.database.db_manager import DatabaseManager
   ```
3. Пересоздайте БД: `python migrate_db.py`
