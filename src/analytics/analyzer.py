"""
Модуль для анализа объявлений Avito
"""
import logging
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AvitoAnalyzer:
    """Класс для анализа объявлений"""

    def __init__(self):
        """Инициализация анализатора"""
        pass

    def analyze_prices(self, ads_data: List[Dict]) -> Dict:
        """
        Анализ цен в объявлениях

        Args:
            ads_data: Список объявлений

        Returns:
            Словарь со статистикой цен
        """
        prices = [ad.get("price") for ad in ads_data if ad.get("price") is not None]

        if not prices:
            return {
                "count": 0,
                "mean": 0,
                "median": 0,
                "min": 0,
                "max": 0,
                "std": 0
            }

        prices_array = np.array(prices)

        return {
            "count": len(prices),
            "mean": float(np.mean(prices_array)),
            "median": float(np.median(prices_array)),
            "min": float(np.min(prices_array)),
            "max": float(np.max(prices_array)),
            "std": float(np.std(prices_array)),
            "quartile_25": float(np.percentile(prices_array, 25)),
            "quartile_75": float(np.percentile(prices_array, 75))
        }

    def analyze_locations(self, ads_data: List[Dict]) -> Dict:
        """
        Анализ распределения по локациям

        Args:
            ads_data: Список объявлений

        Returns:
            Словарь с распределением по локациям
        """
        locations = [ad.get("address") for ad in ads_data if ad.get("address")]

        if not locations:
            return {"total_locations": 0, "top_locations": []}

        location_counts = Counter(locations)

        return {
            "total_locations": len(set(locations)),
            "top_locations": [
                {"location": loc, "count": count}
                for loc, count in location_counts.most_common(10)
            ]
        }

    def analyze_sellers(self, ads_data: List[Dict]) -> Dict:
        """
        Анализ продавцов

        Args:
            ads_data: Список объявлений

        Returns:
            Статистика по продавцам
        """
        sellers = [ad.get("seller") for ad in ads_data if ad.get("seller")]

        if not sellers:
            return {"total_sellers": 0, "top_sellers": []}

        seller_counts = Counter(sellers)

        return {
            "total_sellers": len(set(sellers)),
            "top_sellers": [
                {"seller": seller, "ads_count": count}
                for seller, count in seller_counts.most_common(10)
            ]
        }

    def analyze_keywords(self, ads_data: List[Dict], top_n: int = 20) -> Dict:
        """
        Анализ ключевых слов в заголовках

        Args:
            ads_data: Список объявлений
            top_n: Количество топовых слов

        Returns:
            Словарь с частотой ключевых слов
        """
        # Стоп-слова
        stop_words = {
            'в', 'и', 'на', 'с', 'по', 'для', 'из', 'от', 'до', 'за',
            'у', 'о', 'об', 'к', 'под', 'при', 'без', 'через', 'со'
        }

        all_words = []
        for ad in ads_data:
            title = ad.get("title", "")
            if title:
                # Разбиваем на слова и очищаем
                words = title.lower().split()
                words = [w.strip('.,!?;:()[]{}') for w in words]
                words = [w for w in words if len(w) > 2 and w not in stop_words]
                all_words.extend(words)

        if not all_words:
            return {"total_words": 0, "top_keywords": []}

        word_counts = Counter(all_words)

        return {
            "total_words": len(all_words),
            "unique_words": len(set(all_words)),
            "top_keywords": [
                {"keyword": word, "frequency": count}
                for word, count in word_counts.most_common(top_n)
            ]
        }

    def price_distribution_by_location(self, ads_data: List[Dict]) -> Dict:
        """
        Распределение цен по локациям

        Args:
            ads_data: Список объявлений

        Returns:
            Словарь с ценами по локациям
        """
        location_prices = {}

        for ad in ads_data:
            location = ad.get("address")
            price = ad.get("price")

            if location and price is not None:
                if location not in location_prices:
                    location_prices[location] = []
                location_prices[location].append(price)

        result = {}
        for location, prices in location_prices.items():
            if prices:
                prices_array = np.array(prices)
                result[location] = {
                    "count": len(prices),
                    "mean": float(np.mean(prices_array)),
                    "median": float(np.median(prices_array)),
                    "min": float(np.min(prices_array)),
                    "max": float(np.max(prices_array))
                }

        # Сортируем по количеству объявлений
        sorted_result = dict(
            sorted(result.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
        )

        return sorted_result

    def time_analysis(self, ads_data: List[Dict]) -> Dict:
        """
        Анализ времени публикации объявлений

        Args:
            ads_data: Список объявлений

        Returns:
            Статистика по времени публикации
        """
        dates = [ad.get("published_date") for ad in ads_data if ad.get("published_date")]

        if not dates:
            return {"total_ads_with_dates": 0, "date_distribution": {}}

        date_counts = Counter(dates)

        return {
            "total_ads_with_dates": len(dates),
            "date_distribution": [
                {"date": date, "count": count}
                for date, count in date_counts.most_common(15)
            ]
        }

    def export_to_dataframe(self, ads_data: List[Dict]) -> pd.DataFrame:
        """
        Экспорт данных в pandas DataFrame

        Args:
            ads_data: Список объявлений

        Returns:
            DataFrame с данными
        """
        df = pd.DataFrame(ads_data)

        # Преобразуем типы данных
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')

        if 'views' in df.columns:
            df['views'] = pd.to_numeric(df['views'], errors='coerce')

        return df

    def export_to_csv(self, ads_data: List[Dict], file_path: str):
        """
        Экспорт данных в CSV

        Args:
            ads_data: Список объявлений
            file_path: Путь к файлу
        """
        df = self.export_to_dataframe(ads_data)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        logger.info(f"Данные экспортированы в {file_path}")

    def export_to_json(self, ads_data: List[Dict], file_path: str):
        """
        Экспорт данных в JSON

        Args:
            ads_data: Список объявлений
            file_path: Путь к файлу
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(ads_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Данные экспортированы в {file_path}")

    def generate_report(self, ads_data: List[Dict]) -> Dict:
        """
        Генерация полного отчета по объявлениям

        Args:
            ads_data: Список объявлений

        Returns:
            Словарь с полным отчетом
        """
        logger.info("Генерация отчета...")

        report = {
            "total_ads": len(ads_data),
            "timestamp": datetime.now().isoformat(),
            "price_analysis": self.analyze_prices(ads_data),
            "location_analysis": self.analyze_locations(ads_data),
            "seller_analysis": self.analyze_sellers(ads_data),
            "keyword_analysis": self.analyze_keywords(ads_data),
            "price_by_location": self.price_distribution_by_location(ads_data),
            "time_analysis": self.time_analysis(ads_data)
        }

        logger.info("Отчет сгенерирован")
        return report

    def save_report(self, report: Dict, file_path: str):
        """
        Сохранение отчета в файл

        Args:
            report: Отчет
            file_path: Путь к файлу
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"Отчет сохранен в {file_path}")
