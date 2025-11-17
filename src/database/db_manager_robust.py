"""
Улучшенный менеджер БД с комбинированной стратегией дедупликации
ИСПОЛЬЗУЙТЕ ЭТОТ ФАЙЛ ЕСЛИ test_real_parsing.py ПОКАЗАЛ ЧТО URL ТОЖЕ ДИНАМИЧЕСКИЕ!
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


class DatabaseManagerRobust:
    """Менеджер БД с комбинированной дедупликацией"""

    def __init__(self, db_path: str = "data/avito_ads.db"):
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Директория для БД: {db_file.parent}")

        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._create_tables()

    def _create_tables(self):
        Base.metadata.create_all(self.engine)
        logger.info("Таблицы базы данных созданы/проверены")

    def get_session(self) -> Session:
        return self.SessionLocal()

    def _find_existing_ad(self, session: Session, ad_data: Dict) -> Optional[Advertisement]:
        """
        Комбинированный поиск существующего объявления:
        1. По URL (если есть и стабильный)
        2. По содержимому (title + price + seller + address)
        """
        url = ad_data.get("url")

        # Попытка 1: Поиск по URL
        if url:
            existing = session.query(Advertisement).filter_by(url=url).first()
            if existing:
                logger.debug(f"Найдено по URL: {url[:50]}...")
                return existing

        # Попытка 2: Поиск по содержимому
        title = ad_data.get("title")
        price = ad_data.get("price")
        seller = ad_data.get("seller")
        address = ad_data.get("address")

        if title:  # Title обязателен
            filters = [Advertisement.title == title]

            # Добавляем дополнительные условия если есть данные
            if price is not None:
                filters.append(Advertisement.price == price)
            if seller:
                filters.append(Advertisement.seller == seller)
            if address:
                filters.append(Advertisement.address == address)

            existing = session.query(Advertisement).filter(and_(*filters)).first()
            if existing:
                logger.debug(f"Найдено по содержимому: {title[:50]}...")
                return existing

        return None

    def save_advertisement(self, ad_data: Dict) -> tuple:
        """
        Сохранение с комбинированной дедупликацией

        Returns:
            (Advertisement | None, is_new: bool)
        """
        session = self.get_session()
        try:
            # Ищем существующее объявление
            existing_ad = self._find_existing_ad(session, ad_data)

            if existing_ad:
                # Обновляем существующее
                for key, value in ad_data.items():
                    if key == "id":
                        continue
                    if hasattr(existing_ad, key):
                        setattr(existing_ad, key, value)

                existing_ad.updated_at = datetime.now()
                session.commit()
                logger.debug(f"Обновлено: {ad_data.get('title', '')[:50]}...")
                return (existing_ad, False)
            else:
                # Создаём новое
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
                logger.debug(f"Создано: {ad_data.get('title', '')[:50]}...")
                return (ad, True)

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Ошибка целостности: {e}")
            return (None, False)
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка при сохранении: {e}")
            return (None, False)
        finally:
            session.close()

    def save_advertisements_batch(self, ads_data: List[Dict]) -> dict:
        """Массовое сохранение"""
        created_count = 0
        updated_count = 0
        failed_count = 0

        for ad_data in ads_data:
            ad, is_new = self.save_advertisement(ad_data)
            if ad:
                if is_new:
                    created_count += 1
                else:
                    updated_count += 1
            else:
                failed_count += 1

        logger.info(f"Создано: {created_count}, обновлено: {updated_count}, ошибок: {failed_count}")
        return {
            'created': created_count,
            'updated': updated_count,
            'failed': failed_count
        }

    # Остальные методы - копируем из db_manager.py
    def get_advertisement(self, ad_id: str) -> Optional[Advertisement]:
        session = self.get_session()
        try:
            return session.query(Advertisement).filter_by(ad_id=ad_id).first()
        finally:
            session.close()

    def get_all_advertisements(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "parsed_at"
    ) -> List[Advertisement]:
        session = self.get_session()
        try:
            query = session.query(Advertisement)
            if hasattr(Advertisement, order_by):
                query = query.order_by(desc(getattr(Advertisement, order_by)))
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

            return session.query(Advertisement).filter(and_(*filters)).all()
        finally:
            session.close()

    def save_search_query(self, query: str, location: str, ads_found: int):
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
        session = self.get_session()
        try:
            total_ads = session.query(Advertisement).count()
            active_ads = session.query(Advertisement).filter_by(is_active=True).count()
            total_queries = session.query(SearchQuery).count()

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
        return [ad.to_dict() for ad in ads]
