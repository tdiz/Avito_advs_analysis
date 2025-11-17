# Avito Ads Analysis Bot

Бот для парсинга и анализа объявлений на Avito с возможностью сохранения данных в базу и построения аналитических отчетов.

## Возможности

- Парсинг объявлений по поисковому запросу
- Поддержка различных локаций (города, регионы, вся Россия)
- Сохранение данных в SQLite базу данных
- Анализ цен, локаций, продавцов
- Анализ ключевых слов в объявлениях
- Экспорт данных в CSV и JSON форматы
- Генерация аналитических отчетов

## Структура проекта

```
Avito_advs_analysis/
├── src/
│   ├── parsers/
│   │   ├── __init__.py
│   │   └── avito_parser.py      # Модуль парсинга Avito
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py             # Модели базы данных
│   │   └── db_manager.py         # Менеджер БД
│   ├── analytics/
│   │   ├── __init__.py
│   │   └── analyzer.py           # Модуль анализа данных
│   └── utils/
│       ├── __init__.py
│       └── logger.py             # Настройка логирования
├── data/                         # Директория для БД и данных
├── logs/                         # Логи работы бота
├── config/
│   └── config.yaml              # Конфигурация
├── main.py                      # Главный файл
├── requirements.txt             # Зависимости
└── README.md                    # Документация
```

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd Avito_advs_analysis
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
# или
venv\Scripts\activate     # Для Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Установка ChromeDriver

ChromeDriver устанавливается автоматически при первом запуске через `webdriver-manager`.

## Использование

### Способы запуска

```bash
# Рекомендуемый способ (через run.py)
python run.py --query "ноутбук" --location "moskva" --pages 2

# Или напрямую (требуется правильный PYTHONPATH)
python main.py --query "ноутбук" --location "moskva" --pages 2

# Или установить как пакет и использовать команду
pip install -e .
avito-bot --query "ноутбук" --location "moskva" --pages 2
```

### Базовый запуск

Поиск объявлений с ноутбуками в Москве:

```bash
python run.py --query "ноутбук" --location "moskva" --pages 2
```

### Расширенное использование

```bash
python run.py \
  --query "ноутбук" \
  --location "moskva" \
  --pages 3 \
  --headless \
  --analyze \
  --export-csv data/results.csv \
  --export-json data/results.json \
  --report data/report.json
```

### Работа с данными из БД (без парсинга)

Анализировать уже собранные данные без повторного парсинга:

```bash
# Анализ данных из БД
python run.py --query "ноутбук" --from-db --analyze

# Экспорт из БД с фильтрацией по цене
python run.py --query "ноутбук" --from-db --min-price 30000 --max-price 100000 --export-csv filtered.csv
```

### Параметры командной строки

| Параметр | Описание | Обязательный | Значение по умолчанию |
|----------|----------|--------------|----------------------|
| `--query` | Поисковый запрос | Да* | - |
| `--location` | Локация (moskva, sankt-peterburg, rossiya) | Нет | rossiya |
| `--pages` | Количество страниц для парсинга | Нет | 1 |
| `--from-db` | Использовать данные из БД (без парсинга) | Нет | False |
| `--min-price` | Минимальная цена для фильтрации (только с --from-db) | Нет | - |
| `--max-price` | Максимальная цена для фильтрации (только с --from-db) | Нет | - |
| `--headless` | Запуск браузера в headless режиме | Нет | False |
| `--analyze` | Выполнить анализ данных | Нет | False |
| `--export-csv` | Путь к CSV файлу для экспорта | Нет | - |
| `--export-json` | Путь к JSON файлу для экспорта | Нет | - |
| `--report` | Путь к файлу для сохранения отчета | Нет | - |
| `--db-path` | Путь к базе данных | Нет | data/avito_ads.db |

## Примеры использования

### Пример 1: Простой парсинг

```bash
python run.py --query "iPhone 15" --location "moskva"
```

### Пример 2: Парсинг с анализом

```bash
python run.py --query "квартира" --location "sankt-peterburg" --pages 5 --analyze
```

### Пример 3: Парсинг с экспортом

```bash
python run.py \
  --query "автомобиль Toyota" \
  --location "rossiya" \
  --pages 3 \
  --export-csv results.csv \
  --export-json results.json
```

### Пример 4: Полный анализ с отчетом

```bash
python run.py \
  --query "MacBook" \
  --location "moskva" \
  --pages 5 \
  --headless \
  --analyze \
  --report analysis_report.json
```

### Пример 5: Анализ данных из БД (без парсинга)

```bash
# Сначала собираем данные
python run.py --query "ноутбук" --location "moskva" --pages 3

# Потом анализируем без повторного парсинга
python run.py --query "ноутбук" --from-db --analyze --report laptop_report.json
```

### Пример 6: Фильтрация и экспорт из БД

```bash
# Экспорт только дорогих ноутбуков из БД
python run.py --query "ноутбук" --from-db \
  --min-price 100000 \
  --max-price 200000 \
  --export-csv expensive_laptops.csv \
  --analyze
```

## Возможные локации

- `moskva` - Москва
- `sankt-peterburg` - Санкт-Петербург
- `ekaterinburg` - Екатеринбург
- `novosibirsk` - Новосибирск
- `rossiya` - Вся Россия
- И другие города (проверяйте URL на Avito)

## Структура базы данных

### Таблица `advertisements`

Хранит информацию об объявлениях:

- `id` - Внутренний ID
- `ad_id` - ID объявления на Avito
- `title` - Заголовок
- `price` - Цена
- `url` - Ссылка на объявление
- `description` - Краткое описание
- `full_description` - Полное описание
- `address` - Адрес
- `published_date` - Дата публикации
- `seller` - Продавец
- `views` - Количество просмотров
- `characteristics` - Характеристики (JSON)
- `images` - Изображения (JSON)
- `parsed_at` - Дата парсинга
- `updated_at` - Дата обновления
- `is_active` - Активно ли объявление

### Таблица `search_queries`

Хранит историю поисковых запросов:

- `id` - ID запроса
- `query` - Поисковый запрос
- `location` - Локация
- `ads_found` - Найдено объявлений
- `created_at` - Дата запроса

## Анализ данных

При использовании флага `--analyze` бот предоставляет следующую статистику:

### Анализ цен
- Количество объявлений с ценой
- Средняя цена
- Медианная цена
- Минимальная и максимальная цена
- Стандартное отклонение
- Квартили

### Анализ локаций
- Топ-10 локаций по количеству объявлений
- Распределение цен по локациям

### Анализ ключевых слов
- Топ-20 самых частых слов в заголовках

### Анализ продавцов
- Топ-10 продавцов по количеству объявлений

## Экспорт данных

### CSV экспорт

```bash
python main.py --query "смартфон" --export-csv data/smartphones.csv
```

Создает CSV файл со всеми полями объявлений.

### JSON экспорт

```bash
python main.py --query "смартфон" --export-json data/smartphones.json
```

Создает JSON файл с массивом объявлений.

## Логирование

Логи сохраняются в директорию `logs/` с именем формата:
```
avito_bot_YYYYMMDD.log
```

Уровни логирования настраиваются в `config/config.yaml`.

## Использование как библиотеки

Вы можете использовать модули бота в своих скриптах:

```python
from src.parsers.avito_parser import AvitoParser
from src.database.db_manager import DatabaseManager
from src.analytics.analyzer import AvitoAnalyzer

# Парсинг
with AvitoParser(headless=True) as parser:
    ads = parser.search_ads(query="ноутбук", location="moskva", max_pages=2)

# Сохранение в БД
db = DatabaseManager()
db.save_advertisements_batch(ads)

# Анализ
analyzer = AvitoAnalyzer()
report = analyzer.generate_report(ads)
print(report)
```

## Ограничения и рекомендации

1. **Соблюдайте robots.txt** - используйте задержки между запросами
2. **Не перегружайте сервер** - ограничивайте количество страниц
3. **Используйте headless режим** - для экономии ресурсов
4. **Проверяйте captcha** - Avito может показывать капчу при частых запросах
5. **Используйте VPN** - если получаете блокировки

## Решение проблем

### Проблема: ChromeDriver не найден

**Решение**: ChromeDriver устанавливается автоматически. Убедитесь, что у вас есть доступ к интернету.

### Проблема: Элементы не найдены на странице

**Решение**: Avito может менять структуру HTML. Проверьте актуальность селекторов в `avito_parser.py`.

### Проблема: Captcha

**Решение**: Увеличьте задержки между запросами, используйте VPN, уменьшите количество страниц.

### Проблема: Timeout

**Решение**: Увеличьте таймауты в `config/config.yaml`.

## Лицензия

MIT License

## Отказ от ответственности

Этот проект создан исключительно в образовательных целях. При использовании убедитесь, что вы соблюдаете правила использования Avito и применимое законодательство.

## Контакты

Если у вас есть вопросы или предложения, создайте issue в репозитории проекта.

## Changelog

### v1.0.0 (2024)
- Первая версия бота
- Парсинг объявлений Avito
- Сохранение в SQLite
- Базовый анализ данных
- Экспорт в CSV/JSON
