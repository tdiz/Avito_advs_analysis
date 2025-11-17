# Стратегии дедупликации объявлений Avito

## Проблема
Avito может генерировать динамические идентификаторы. Нужна надёжная стратегия определения дубликатов.

## Возможные стратегии

### Стратегия 1: По URL (текущая реализация)
```python
url = Column(String(1000), unique=True, nullable=False, index=True)
```

**Предположение:** URL объявления стабилен
**Проверка:** Запустите `python test_real_parsing.py`

**Плюсы:**
- Простая реализация
- Если URL стабилен - 100% точность

**Минусы:**
- Если URL содержит сессионные параметры - не сработает
- Пока НЕ ПРОВЕРЕНО на реальных данных

---

### Стратегия 2: По комбинации полей (Title + Price + Seller)
```python
# Удаляем UNIQUE с URL
# Добавляем проверку по нескольким полям

def find_existing_ad(session, ad_data):
    return session.query(Advertisement).filter(
        Advertisement.title == ad_data['title'],
        Advertisement.price == ad_data['price'],
        Advertisement.seller == ad_data['seller']
    ).first()
```

**Плюсы:**
- Не зависит от внешних ID
- Работает даже если URL/ad_id динамические

**Минусы:**
- Ложные совпадения (разные объявления с одинаковым названием/ценой)
- Не поймает изменение цены (создаст дубликат)

---

### Стратегия 3: По hash нескольких полей
```python
import hashlib

def calculate_ad_hash(title, price, seller, address):
    """Уникальный хэш объявления"""
    data = f"{title}|{price}|{seller}|{address}".lower()
    return hashlib.md5(data.encode()).hexdigest()

# В модели:
content_hash = Column(String(32), unique=True, index=True)
```

**Плюсы:**
- Учитывает несколько полей
- Быстрый поиск по индексу

**Минусы:**
- Любое изменение создаёт новый hash (даже обновление цены)
- Коллизии (хоть и редкие)

---

### Стратегия 4: Комбинированная (рекомендуется)
```python
# 1. Сначала пробуем по URL
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

**Плюсы:**
- Работает если URL стабилен
- Fallback если URL меняется
- Обновляет существующие объявления

**Минусы:**
- Сложнее реализация
- Медленнее (два запроса)

---

## Что делать СЕЙЧАС?

1. **Запустите тест:**
   ```bash
   python test_real_parsing.py
   ```

2. **Посмотрите результат:**
   - Если URL одинаковые → текущая реализация OK ✓
   - Если URL разные → нужна Стратегия 4 (комбинированная)

3. **Сообщите мне результат теста** - я доработаю код под реальное поведение Avito

---

## Текущая реализация
Используется **Стратегия 1 (по URL)** в файлах:
- `src/database/models.py:24` - `url` с `unique=True`
- `src/database/db_manager.py:60` - поиск по `filter_by(url=...)`

**Статус:** ⚠️ Требует проверки на реальных данных!
