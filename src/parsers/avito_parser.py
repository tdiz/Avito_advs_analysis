"""
Модуль для парсинга объявлений с Avito
"""
import time
import random
import logging
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


logger = logging.getLogger(__name__)


class AvitoParser:
    """Класс для парсинга объявлений с Avito"""

    BASE_URL = "https://www.avito.ru"

    def __init__(self, headless: bool = True, user_agent: Optional[str] = None):
        """
        Инициализация парсера

        Args:
            headless: Запускать браузер в headless режиме
            user_agent: Пользовательский User-Agent
        """
        self.headless = headless
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self.driver = None

    def _setup_driver(self):
        """Настройка Selenium WebDriver с максимальной маскировкой"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless=new")  # Новый headless режим

        # User-Agent
        chrome_options.add_argument(f"user-agent={self.user_agent}")

        # Базовые антидетект параметры
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")

        # Дополнительные флаги для маскировки
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        chrome_options.add_argument("--disable-site-isolation-trials")

        # Отключаем обнаружение автоматизации
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Preferences для более реалистичного поведения
        prefs = {
            "profile.default_content_setting_values.notifications": 2,  # Блокируем уведомления
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        chrome_options.add_experimental_option("prefs", prefs)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Продвинутая маскировка через JS
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                // Убираем webdriver флаг
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

                // Подделываем параметры браузера
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru', 'en-US', 'en']});

                // Подделываем Chrome runtime
                window.chrome = {runtime: {}};

                // Маскируем permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({state: Notification.permission}) :
                        originalQuery(parameters)
                );
            """
        })

        logger.info("WebDriver настроен в стелс-режиме")

    def search_ads(
        self,
        query: str,
        location: str = "rossiya",
        max_pages: int = 1,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Поиск объявлений по запросу

        Args:
            query: Поисковый запрос
            location: Локация (например, 'moskva', 'sankt-peterburg')
            max_pages: Максимальное количество страниц для парсинга
            limit: Максимальное количество объявлений (останавливается после достижения)

        Returns:
            Список словарей с информацией об объявлениях
        """
        if not self.driver:
            self._setup_driver()

        all_ads = []

        # Прогресс-бар для страниц
        with tqdm(total=max_pages, desc="Парсинг страниц", unit="стр") as pbar:
            for page in range(1, max_pages + 1):
                pbar.set_description(f"Страница {page}/{max_pages}")

                # Формируем URL для поиска
                search_url = f"{self.BASE_URL}/{location}?q={query}&p={page}"
                logger.info(f"Парсинг URL: {search_url}")

                try:
                    self.driver.get(search_url)
                    # Случайная задержка 3-6 секунд (имитация человека)
                    delay = random.uniform(3, 6)
                    pbar.set_postfix({"загрузка": f"{delay:.1f}с"})
                    time.sleep(delay)

                    # Парсим объявления на странице
                    ads = self._parse_page()
                    all_ads.extend(ads)

                    pbar.set_postfix({"найдено": len(ads), "всего": len(all_ads)})
                    logger.info(f"Найдено {len(ads)} объявлений на странице {page}")

                    # Проверяем лимит
                    if limit and len(all_ads) >= limit:
                        logger.info(f"Достигнут лимит: {limit} объявлений")
                        all_ads = all_ads[:limit]  # Обрезаем до нужного количества
                        pbar.update(max_pages - page + 1)  # Завершаем прогресс-бар
                        break

                    pbar.update(1)

                    # Случайная пауза между страницами 5-10 секунд
                    if page < max_pages:
                        delay = random.uniform(5, 10)
                        pbar.set_postfix({"пауза": f"{delay:.1f}с"})
                        logger.info(f"Пауза {delay:.1f} сек перед следующей страницей...")
                        time.sleep(delay)

                except Exception as e:
                    logger.error(f"Ошибка при парсинге страницы {page}: {e}")
                    pbar.update(1)
                    continue

        logger.info(f"Всего найдено {len(all_ads)} объявлений")
        return all_ads

    def _parse_page(self) -> List[Dict]:
        """
        Парсинг одной страницы объявлений

        Returns:
            Список объявлений
        """
        ads = []

        try:
            # Проверка на блокировку/капчу
            page_source = self.driver.page_source

            # DEBUG: Сохраняем HTML и скриншот для анализа
            if "Доступ ограничен" in page_source or "проблема с IP" in page_source:
                import os
                from pathlib import Path
                debug_dir = Path("debug")
                debug_dir.mkdir(exist_ok=True)

                # Сохраняем HTML
                with open(debug_dir / "page_blocked.html", "w", encoding="utf-8") as f:
                    f.write(page_source)

                # Сохраняем скриншот
                self.driver.save_screenshot(str(debug_dir / "page_blocked.png"))

                logger.error("❌ ОБНАРУЖЕНА БЛОКИРОВКА AVITO!")
                logger.error(f"Debug файлы сохранены в: {debug_dir.absolute()}")
                logger.error("  - page_blocked.html (HTML страницы)")
                logger.error("  - page_blocked.png (скриншот)")
                logger.error("")
                logger.error("Рекомендации:")
                logger.error("  1. Откройте файлы выше чтобы увидеть что видит бот")
                logger.error("  2. Подождите 10-15 минут")
                logger.error("  3. Перезагрузите роутер для получения нового IP")
                logger.error("  4. Используйте VPN/прокси")
                raise ConnectionError("IP заблокирован Avito")

            # Ждем загрузки элементов
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-marker='item']"))
            )

            # Имитация человека: плавный скроллинг страницы
            scroll_pause = random.uniform(0.5, 1.5)
            for i in range(3):  # 3 скролла вниз
                self.driver.execute_script(f"window.scrollBy(0, {random.randint(300, 500)});")
                time.sleep(scroll_pause)

            # Получаем HTML страницы
            soup = BeautifulSoup(page_source, 'lxml')

            # Находим все объявления
            ad_items = soup.find_all(attrs={"data-marker": "item"})

            for item in ad_items:
                try:
                    ad_data = self._extract_ad_data(item)
                    if ad_data:
                        ads.append(ad_data)
                except Exception as e:
                    logger.error(f"Ошибка при извлечении данных объявления: {e}")
                    continue

        except TimeoutException:
            logger.error("Таймаут при загрузке страницы")
        except Exception as e:
            logger.error(f"Ошибка при парсинге страницы: {e}")

        return ads

    def _extract_ad_data(self, item) -> Optional[Dict]:
        """
        Извлечение данных из одного объявления

        Args:
            item: BeautifulSoup элемент объявления

        Returns:
            Словарь с данными объявления
        """
        try:
            # Заголовок
            title_elem = item.find(attrs={"itemprop": "name"})
            title = title_elem.text.strip() if title_elem else None

            # Цена
            price_elem = item.find(attrs={"itemprop": "price"})
            price = None
            if price_elem:
                price_content = price_elem.get("content")
                price = int(price_content) if price_content else None

            # Ссылка
            link_elem = item.find("a", attrs={"itemprop": "url"})
            url = None
            ad_id = None
            if link_elem:
                url = self.BASE_URL + link_elem.get("href")
                # Извлекаем ID объявления из URL
                ad_id = url.split('_')[-1] if '_' in url else None

            # Описание
            description_elem = item.find(attrs={"class": lambda x: x and "item-description" in x})
            description = description_elem.text.strip() if description_elem else None

            # Адрес
            address_elem = item.find(attrs={"class": lambda x: x and "geo-root" in x})
            address = address_elem.text.strip() if address_elem else None

            # Дата публикации
            date_elem = item.find(attrs={"data-marker": "item-date"})
            published_date = date_elem.text.strip() if date_elem else None

            # Продавец
            seller_elem = item.find(attrs={"data-marker": "item-link"})
            seller = seller_elem.text.strip() if seller_elem else None

            ad_data = {
                "id": ad_id,
                "title": title,
                "price": price,
                "url": url,
                "description": description,
                "address": address,
                "published_date": published_date,
                "seller": seller,
                "parsed_at": datetime.now()
            }

            return ad_data

        except Exception as e:
            logger.error(f"Ошибка при извлечении данных: {e}")
            return None

    def get_ad_details(self, ad_url: str) -> Optional[Dict]:
        """
        Получение детальной информации об объявлении

        Args:
            ad_url: URL объявления

        Returns:
            Словарь с детальной информацией
        """
        if not self.driver:
            self._setup_driver()

        try:
            self.driver.get(ad_url)
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Получаем дополнительную информацию
            details = {
                "url": ad_url,
                "full_description": None,
                "images": [],
                "characteristics": {},
                "views": None,
                "seller_info": {}
            }

            # Полное описание
            desc_elem = soup.find(attrs={"itemprop": "description"})
            if desc_elem:
                details["full_description"] = desc_elem.text.strip()

            # Изображения
            img_elems = soup.find_all("img", attrs={"itemprop": "image"})
            details["images"] = [img.get("src") for img in img_elems if img.get("src")]

            # Характеристики
            params = soup.find_all("li", attrs={"class": lambda x: x and "params-paramsList" in x})
            for param in params:
                try:
                    key = param.find(attrs={"class": lambda x: x and "key" in x})
                    value = param.find(attrs={"class": lambda x: x and "value" in x})
                    if key and value:
                        details["characteristics"][key.text.strip()] = value.text.strip()
                except:
                    pass

            # Количество просмотров
            views_elem = soup.find(attrs={"data-marker": "item-view/total-views"})
            if views_elem:
                views_text = views_elem.text.strip()
                try:
                    details["views"] = int(''.join(filter(str.isdigit, views_text)))
                except:
                    pass

            return details

        except Exception as e:
            logger.error(f"Ошибка при получении деталей объявления: {e}")
            return None

    def close(self):
        """Закрытие драйвера"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver закрыт")

    def __enter__(self):
        """Контекстный менеджер"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрытие при выходе из контекста"""
        self.close()
