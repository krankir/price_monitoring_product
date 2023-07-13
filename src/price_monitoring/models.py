from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, TIMESTAMP, Numeric, ForeignKey, Float,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Product(Base):
    """Таблица товара."""

    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    rating = Column(Float, default=0)
    prices = relationship('Price', back_populates="products",
                          passive_deletes=True)


product_tb = Product.__table__


class Price(Base):
    """Таблица мониторинга цены на товар."""

    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column(Numeric, nullable=False)
    price_at = Column(TIMESTAMP, default=datetime.utcnow)
    product_id = Column(Integer, ForeignKey('products.id',
                                            ondelete='CASCADE'), nullable=False)
    products = relationship('Product', back_populates='prices')


price_tb = Price.__table__
