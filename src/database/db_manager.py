"""
Менеджер базы данных для работы с объявлениями
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, desc, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from .models import Base, Advertisement, SearchQuery

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Класс для управления базой данных"""

    def __init__(self, db_path: str = "data/avito_ads.db"):
        """
        Инициализация менеджера БД

        Args:
            db_path: Путь к файлу базы данных
        """
        # Создаём директорию для БД, если её нет
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Директория для БД: {db_file.parent}")

        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._create_tables()

    def _create_tables(self):
        """Создание таблиц в базе данных"""
        Base.metadata.create_all(self.engine)
        logger.info("Таблицы базы данных созданы/проверены")

    def get_session(self) -> Session:
        """Получение сессии базы данных"""
        return self.SessionLocal()

    def save_advertisement(self, ad_data: Dict) -> Optional[Advertisement]:
        """
        Сохранение объявления в базу данных

        Args:
            ad_data: Словарь с данными объявления

        Returns:
            Объект Advertisement или None
        """
        session = self.get_session()
        try:
            # Проверяем, существует ли уже объявление
            existing_ad = session.query(Advertisement).filter_by(
                ad_id=ad_data.get("id")
            ).first()

            if existing_ad:
                # Обновляем существующее объявление
                for key, value in ad_data.items():
                    if key == "id":
                        continue
                    if hasattr(existing_ad, key):
                        setattr(existing_ad, key, value)
                existing_ad.updated_at = datetime.now()
                session.commit()
                logger.info(f"Объявление {ad_data.get('id')} обновлено")
                return existing_ad
            else:
                # Создаем новое объявление
                ad = Advertisement(
                    ad_id=ad_data.get("id"),
                    title=ad_data.get("title"),
                    price=ad_data.get("price"),
                    url=ad_data.get("url"),
                    description=ad_data.get("description"),
                    full_description=ad_data.get("full_description"),
                    address=ad_data.get("address"),
                    published_date=ad_data.get("published_date"),
                    seller=ad_data.get("seller"),
                    seller_info=ad_data.get("seller_info"),
                    views=ad_data.get("views"),
                    characteristics=ad_data.get("characteristics"),
                    images=ad_data.get("images"),
                )
                session.add(ad)
                session.commit()
                logger.info(f"Объявление {ad_data.get('id')} сохранено")
                return ad

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Ошибка целостности данных: {e}")
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка при сохранении объявления: {e}")
            return None
        finally:
            session.close()

    def save_advertisements_batch(self, ads_data: List[Dict]) -> int:
        """
        Массовое сохранение объявлений

        Args:
            ads_data: Список словарей с данными объявлений

        Returns:
            Количество сохраненных объявлений
        """
        saved_count = 0
        for ad_data in ads_data:
            if self.save_advertisement(ad_data):
                saved_count += 1
        logger.info(f"Сохранено {saved_count} из {len(ads_data)} объявлений")
        return saved_count

    def get_advertisement(self, ad_id: str) -> Optional[Advertisement]:
        """
        Получение объявления по ID

        Args:
            ad_id: ID объявления

        Returns:
            Объект Advertisement или None
        """
        session = self.get_session()
        try:
            ad = session.query(Advertisement).filter_by(ad_id=ad_id).first()
            return ad
        finally:
            session.close()

    def get_all_advertisements(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "parsed_at"
    ) -> List[Advertisement]:
        """
        Получение всех объявлений

        Args:
            limit: Максимальное количество объявлений
            offset: Смещение
            order_by: Поле для сортировки

        Returns:
            Список объявлений
        """
        session = self.get_session()
        try:
            query = session.query(Advertisement)

            # Сортировка
            if hasattr(Advertisement, order_by):
                query = query.order_by(desc(getattr(Advertisement, order_by)))

            # Пагинация
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)

            return query.all()
        finally:
            session.close()

    def search_advertisements(
        self,
        query: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        address: Optional[str] = None
    ) -> List[Advertisement]:
        """
        Поиск объявлений по критериям

        Args:
            query: Поисковый запрос (по заголовку/описанию)
            min_price: Минимальная цена
            max_price: Максимальная цена
            address: Адрес

        Returns:
            Список найденных объявлений
        """
        session = self.get_session()
        try:
            filters = [Advertisement.is_active == True]

            if query:
                search_filter = or_(
                    Advertisement.title.ilike(f"%{query}%"),
                    Advertisement.description.ilike(f"%{query}%")
                )
                filters.append(search_filter)

            if min_price is not None:
                filters.append(Advertisement.price >= min_price)

            if max_price is not None:
                filters.append(Advertisement.price <= max_price)

            if address:
                filters.append(Advertisement.address.ilike(f"%{address}%"))

            ads = session.query(Advertisement).filter(and_(*filters)).all()
            return ads
        finally:
            session.close()

    def save_search_query(self, query: str, location: str, ads_found: int):
        """
        Сохранение поискового запроса в историю

        Args:
            query: Поисковый запрос
            location: Локация
            ads_found: Количество найденных объявлений
        """
        session = self.get_session()
        try:
            search = SearchQuery(
                query=query,
                location=location,
                ads_found=ads_found
            )
            session.add(search)
            session.commit()
            logger.info(f"Поисковый запрос '{query}' сохранен")
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка при сохранении запроса: {e}")
        finally:
            session.close()

    def get_statistics(self) -> Dict:
        """
        Получение статистики по базе данных

        Returns:
            Словарь со статистикой
        """
        session = self.get_session()
        try:
            total_ads = session.query(Advertisement).count()
            active_ads = session.query(Advertisement).filter_by(is_active=True).count()
            total_queries = session.query(SearchQuery).count()

            # Средняя цена
            avg_price = session.query(Advertisement).filter(
                Advertisement.price.isnot(None)
            ).with_entities(Advertisement.price).all()
            avg_price_value = sum(p[0] for p in avg_price) / len(avg_price) if avg_price else 0

            return {
                "total_advertisements": total_ads,
                "active_advertisements": active_ads,
                "total_search_queries": total_queries,
                "average_price": round(avg_price_value, 2)
            }
        finally:
            session.close()

    def export_to_dict(self, ads: List[Advertisement]) -> List[Dict]:
        """
        Экспорт объявлений в список словарей

        Args:
            ads: Список объявлений

        Returns:
            Список словарей
        """
        return [ad.to_dict() for ad in ads]
