"""
Модуль для парсинга объявлений с Avito
"""
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import requests
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
        """Настройка Selenium WebDriver"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument(f"user-agent={self.user_agent}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")

        # Отключаем обнаружение автоматизации
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Убираем признак WebDriver
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        logger.info("WebDriver настроен успешно")

    def search_ads(
        self,
        query: str,
        location: str = "rossiya",
        max_pages: int = 1
    ) -> List[Dict]:
        """
        Поиск объявлений по запросу

        Args:
            query: Поисковый запрос
            location: Локация (например, 'moskva', 'sankt-peterburg')
            max_pages: Максимальное количество страниц для парсинга

        Returns:
            Список словарей с информацией об объявлениях
        """
        if not self.driver:
            self._setup_driver()

        all_ads = []

        for page in range(1, max_pages + 1):
            logger.info(f"Парсинг страницы {page} из {max_pages}")

            # Формируем URL для поиска
            search_url = f"{self.BASE_URL}/{location}?q={query}&p={page}"
            logger.info(f"Парсинг URL: {search_url}")

            try:
                self.driver.get(search_url)
                time.sleep(2)  # Ждем загрузки страницы

                # Парсим объявления на странице
                ads = self._parse_page()
                all_ads.extend(ads)

                logger.info(f"Найдено {len(ads)} объявлений на странице {page}")

                # Пауза между запросами
                time.sleep(3)

            except Exception as e:
                logger.error(f"Ошибка при парсинге страницы {page}: {e}")
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
            # Ждем загрузки элементов
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-marker='item']"))
            )

            # Получаем HTML страницы
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

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
