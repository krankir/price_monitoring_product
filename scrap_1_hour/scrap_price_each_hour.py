from datetime import datetime
import schedule
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Product, Price
from config import DATABASE_URI, SEC
from scrap_data.scrap_main import ScrapDataProduct


engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

URL_LIST = []

def scrap_one_hour():
    """Периодическое получение цены и занесение значений в базу данных."""
    session = Session()
    for i in session.query(Product).all():
        URL_LIST.append(i.url)


    for i in URL_LIST:
        price = ScrapDataProduct(i).scrap_price()
        session = Session()
        product = session.query(Product).filter(Product.url == i).first()
        price_at = datetime.utcnow()
        new_price = Price(price=price,
                          price_at=price_at,
                          product_id=product.id)
        session.add(new_price)
        session.commit()
        print('[INFO] Data was successfully inserted')

def main():
    """Планировщик выполнения скрипта"""
    # schedule.every().hour.do(scrap_one_hour)
    schedule.every(SEC).seconds.do(scrap_one_hour)

    while True:
        schedule.run_pending()

if __name__ == '__main__':
    main()
