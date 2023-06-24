import json

import requests
import re

from scrap_data.cookies_and_headers import cookies, headers, cookies_price, \
    headers_price
from scrap_data.models import Item


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
        product_id = self.__get_product_id()
        print(product_id)
        params = {'productId': product_id}
        response = requests.get('https://www.mvideo.ru/bff/product-details',
                                params=params,
                                cookies=cookies,
                                headers=headers,
                                )
        print(response.text)
        products_infos = Item.parse_obj(response.json()['body'])
        data_dict = {
            'name': products_infos.modelName,
            'description': products_infos.description,
            'rating': round(products_infos.rating.get('star'), 2)
        }
        with open('data.json', 'a') as file:
            json.dump(data_dict, file, indent=4, ensure_ascii=False)

    def scrap_price(self):
        product_id = self.__get_product_id()
        print(product_id)
        params_price = {
            'productIds': product_id,
            'isPromoApplied': 'true',
            'addBonusRubles': 'true',
        }
        response_pr = requests.get(
            'https://www.mvideo.ru/bff/products/prices',
            params=params_price,
            cookies=cookies_price,
            headers=headers_price,
        )
        price = (response_pr.json()).get('body').get('materialPrices')[0].get(
            'price').get('salePrice')
        print(price)


if __name__ == '__main__':
    url = input('Введите url товара:')
    # ScrapDataProduct(url).scrap()
    ScrapDataProduct(url).scrap_price()
