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
    for product in session.query(Product).all():
        URL_LIST.append(product.url)

    session.close()

    current_time = datetime.utcnow()
    new_prices = []

    for url in URL_LIST:
        price = ScrapDataProduct(url).scrap_price()

        product = session.query(Product).filter(Product.url == url).first()
        new_price = Price(
            price=price, price_at=current_time, product_id=product.id)
        new_prices.append(new_price)

    session = Session()
    session.add_all(new_prices)
    session.commit()
    session.close()

    print('[INFO] Data was successfully inserted')


def main():
    """Планировщик выполнения скрипта"""
    # schedule.every().hour.do(scrap_one_hour)
    schedule.every(SEC).seconds.do(scrap_one_hour)

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    main()
