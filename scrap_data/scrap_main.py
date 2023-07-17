import os

import re
import requests
from dotenv import load_dotenv
from scrap_data.cookies_and_headers import (
    cookies, headers, cookies_price, headers_price,
)
from scrap_data.models import Item


load_dotenv()

PROXY_MANAGER_API_KEY = os.getenv('PROXY_MANAGER_API_KEY')

class ScrapDataProduct:
    """Получения информации о товаре."""

    def __init__(self, url: str):
        self.url = url

    def __get_product_id(self):
        """Получение id товара."""
        regex = '(\d+)$'
        product_ids = re.split(regex, self.url)
        product_id = product_ids[1]
        return product_id

    def scrap(self):
        """Получение данных о продукте."""
        product_id = self.__get_product_id()
        params = {
            'productId': product_id,
            'token': PROXY_MANAGER_API_KEY,
            'type': 'socks5',
            'count': 1,
            'country': 'ru',
        }
        response = requests.get('https://www.mvideo.ru/bff/product-details',
                                params=params,
                                cookies=cookies,
                                headers=headers,
                                timeout=10,
                                )
        products_infos = Item.parse_obj(response.json()['body'])
        data_dict = {
            'name': products_infos.modelName,
            'description': re.sub(
                '^\s+|\n|\r|\s+$|<br>|<p>|</p>', ' ',
                products_infos.description),
            'rating': round(products_infos.rating.get('star'), 2)
        }
        return data_dict

    def scrap_price(self):
        """Получение цены продукта."""
        product_id = self.__get_product_id()
        print(product_id)
        params_price = {
            'productIds': product_id,
            'isPromoApplied': 'true',
            'addBonusRubles': 'true',
            'token': PROXY_MANAGER_API_KEY,
            'type': 'socks5',
            'count': 1,
            'country': 'ru',
        }
        response_pr = requests.get(
            'https://www.mvideo.ru/bff/products/prices',
            params=params_price,
            cookies=cookies_price,
            headers=headers_price,
            timeout=10,
        )
        price = (response_pr.json()).get('body').get('materialPrices')[0].get(
            'price').get('salePrice')
        return price
