from datetime import datetime

import psycopg2 as ps
import schedule

from config import DATABASE_URI, SEC
from scrap_data.scrap_main import ScrapDataProduct

con = ps.connect(DATABASE_URI)
con.autocommit = True

URL_LIST = []


def scrap_one_hour():
    with con.cursor() as cursor:
        cursor.execute(
            """SELECT products.url FROM products"""
        )
        for i in cursor:
            URL_LIST.append(i[0])

    with con.cursor() as cursor:
        for i in URL_LIST:
            price = ScrapDataProduct(i).scrap_price()
            cursor.execute(
                """SELECT products.id FROM products WHERE products.url = %s""",
                (i,)
            )
            product_id = cursor.fetchone()[0]
            price_at = datetime.utcnow()
            cursor.execute(
                """INSERT INTO prices (price, price_at, product_id) VALUES (%s, %s, %s)""",
                (price, price_at, product_id))
            print('[INFO] Data was successfully inserted')


def main():
    """Планировщик выполнения скрипта"""
    # schedule.every().hour.do(scrap_one_hour)
    schedule.every(SEC).seconds.do(scrap_one_hour)

    while True:
        schedule.run_pending()


if __name__ == '__main__':
    main()

