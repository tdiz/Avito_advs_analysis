"""
Модели базы данных для хранения объявлений Avito
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime,
    Boolean, JSON, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Advertisement(Base):
    """Модель для хранения объявлений"""

    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_id = Column(String(255), nullable=True, index=True)  # Может быть динамическим
    title = Column(String(500), nullable=False)
    price = Column(Float, nullable=True)
    url = Column(String(1000), unique=True, nullable=False, index=True)  # URL - стабильный идентификатор
    description = Column(Text, nullable=True)
    full_description = Column(Text, nullable=True)
    address = Column(String(500), nullable=True)
    published_date = Column(String(100), nullable=True)
    seller = Column(String(200), nullable=True)
    seller_info = Column(JSON, nullable=True)
    views = Column(Integer, nullable=True)
    characteristics = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    parsed_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Advertisement(id={self.ad_id}, title={self.title[:30]}...)>"

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "id": self.id,
            "ad_id": self.ad_id,
            "title": self.title,
            "price": self.price,
            "url": self.url,
            "description": self.description,
            "full_description": self.full_description,
            "address": self.address,
            "published_date": self.published_date,
            "seller": self.seller,
            "seller_info": self.seller_info,
            "views": self.views,
            "characteristics": self.characteristics,
            "images": self.images,
            "parsed_at": self.parsed_at.isoformat() if self.parsed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }


class SearchQuery(Base):
    """Модель для хранения истории поисковых запросов"""

    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String(500), nullable=False)
    location = Column(String(100), nullable=True)
    ads_found = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<SearchQuery(query={self.query}, ads_found={self.ads_found})>"
