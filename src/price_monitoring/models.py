from datetime import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, Numeric

from src.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    price = Column(Numeric)
    price_at = Column(TIMESTAMP, default=datetime.utcnow)
    name = Column(String)
    description = Column(String)
    rating = Column(Integer, default=0)
