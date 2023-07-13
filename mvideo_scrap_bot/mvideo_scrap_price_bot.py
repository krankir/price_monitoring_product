import os
import time

from aiogram.types import (
    KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from dotenv import load_dotenv
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.markdown import hbold, hlink
from config import DATABASE_URI
from models import Product, Price
from scrap_data.scrap_main import ScrapDataProduct
from sqlalchemy import desc, create_engine, select
from sqlalchemy.orm import sessionmaker


load_dotenv()

engine = create_engine(DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)

bot = Bot(token=os.getenv('TOKEN'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

PRODUCT_LINC = ''
NAME_PRODUCT_DELETE = ''
NAME_PRODUCT_PRICE = ''

async def on_startup(_):
    """Действия перед запуском бота."""
    print('Бот вышел в онлайн...')


async def on_shutdown(_):
    """Действия после остановки бота."""
    print('Закрываю соединение с БД')

b1 = KeyboardButton('Получение списка всех товаров')
b2 = KeyboardButton('Удаление товара')
b3 = KeyboardButton('Добавить товар на мониторинг')
b4 = KeyboardButton('Получение истории цен на товар')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.row(b1, b2).add(b3).add(b4)


@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    """Стартовый обработчик"""
    await message.answer(f'Добрый день {message.from_user.first_name}! '
                         f'Для добавления товара на мониторинг, напишите ссылку'
                         f' на товар.Или воспользуйтесь меню ⬇',
                         reply_markup=kb_client,
                         )

price_product = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(
    text='Да, показать цену этого товара', callback_data='get_price'))

@dp.message_handler(
    lambda message: 'Получение истории цен на товар' in message.text)
async def delete_product(message: types.Message):
    """История изменения цен на товар."""
    await message.answer('Напишите в чат: история цен (id товара)')

@dp.message_handler(lambda message: 'история цен' in message.text.lower())
async def delete_product(message: types.Message):
    """История изменения цен на товар."""
    global NAME_PRODUCT_PRICE
    NAME_PRODUCT_PRICE = message.text[11:].strip()
    await message.answer(
        f'Показать цену товара c id? {NAME_PRODUCT_PRICE}',
        reply_markup=price_product,
    )

@dp.callback_query_handler(text='get_price')
async def get_price_product(callback: types.CallbackQuery):
    """История изменения цен на товар."""
    await callback.answer('Показать цены на товар')
    session = Session()
    product = session.query(Product).filter(
        Product.id == NAME_PRODUCT_PRICE).first()
    if product is None:
        await callback.message.answer(
            '❌Товара с таким id ещё нету в списке, сначала добавьте'
            ' товар')
    else:
        product_prices = select(Price).filter(
            Price.product_id == NAME_PRODUCT_PRICE).order_by(
            desc(Price.price_at)
        )
        res = session.scalars(product_prices)
        for index, product in enumerate(res):
            card = f'{hbold("Товар c id: ")} {NAME_PRODUCT_PRICE}\n' \
                   f'{hbold("Цена: ")} {product.price}🔥\n' \
                   f'{hbold("Дата и время обновления: ")} {product.price_at}\n'

            if index  == 20:
                break

            await callback.message.answer(card)

@dp.message_handler(
    lambda message: 'Получение списка всех товаров' in message.text)
async def all_product(message: types.Message):
    """Просмотр всех товаров на мониторинге."""
    await message.answer('Пожалуйста подождите⌛...')
    session = Session()
    users = session.query(Product).all()
    for index, product in enumerate(users):
        linc = hlink(product.name, product.url)
        card = f'{hbold("Ссылка: ")} {linc}\n' \
               f'{hbold("id: ")} {product.id}\n' \
               f'{hbold("Рейтинг: ")} {product.rating}🔥\n' \
               f'{hbold("Название: ")} {product.name}\n' \
               f'{hbold("Описание: ")} {product.description}\n'

        #  Защита от бана за флуд.
        if index % 20 == 0:
            time.sleep(3)

        await message.answer(card)

del_product_inline = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton(
    text='Да, удалить с мониторинга', callback_data='delet'))

@dp.message_handler(lambda message: 'Удаление товара' in message.text)
async def delete_product(message: types.Message):
    """Удаление товара из мониторинга."""
    await message.answer('Напишите в чат:'
                         ' удалить (id товара из карточки)')

@dp.message_handler(lambda message: 'удалить' in message.text.lower())
async def delete_product(message: types.Message):
    """Удаление товара из мониторинга."""
    global NAME_PRODUCT_DELETE
    NAME_PRODUCT_DELETE = message.text[7:].strip()
    await message.answer(
        f'Вы уверены что хотите удалить именно этот товар? {message.text[7:]}',
        reply_markup=del_product_inline,
    )

@dp.callback_query_handler(text='delet')
async def www_pars(callback: types.CallbackQuery):
    """Удаление товара из мониторинга."""
    session = Session()
    product_delete = session.get(Product, NAME_PRODUCT_DELETE)
    session.delete(product_delete)
    session.commit()
    await callback.message.answer('Товар успешно удалён 🗑')

add_products_inline = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(
        text='Добавить товар на мониторинг', callback_data='scrap'))

@dp.message_handler(
    lambda message: 'Добавить товар на мониторинг' in message.text)
async def delete_product(message: types.Message):
    """Добавление товара на мониторинг."""
    await message.answer('Напишите в чат: ссылку на товар с сайта М.видео')

@dp.message_handler(
    lambda message: 'https://www.mvideo.ru/products/' in message.text)
async def www_par(message: types.Message):
    """Добавление товара на мониторинг."""
    global PRODUCT_LINC
    PRODUCT_LINC = message.text
    await message.answer(
        'Вы уверены что хотите добавить именно этот товар? ',
        reply_markup=add_products_inline,
    )

@dp.callback_query_handler(text='scrap')
async def www_pars(callback: types.CallbackQuery):
    """Добавление товара на мониторинг."""
    await callback.answer('Начать добавление?', show_alert=True)
    product = ScrapDataProduct(PRODUCT_LINC).scrap()
    linc = str(PRODUCT_LINC)
    name = product['name']
    description = product['description']
    rating = product['rating']
    session = Session()
    product = session.query(Product).filter(
        Product.url == linc).first()
    if product is not None:
        await callback.message.answer(
            '❌ Данный товар уже присутствует на мониторинге.')
    else:
        new_product = Product(url=linc,
                              name=name,
                              description=description,
                              rating=rating,
                              )
        session.add(new_product)
        session.commit()
        await callback.message.answer('Товар успешно добавлен✅')

@dp.message_handler()
async def echo_send(message: types.Message):
    """Эхо обработчик."""
    await message.reply(
        'Неверная команда, прочтите ещё раз какой должен быть запрос и'
        ' повторите попытку...')

def main():
    executor.start_polling(dp, skip_updates=True,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown,
                           )

if __name__ == '__main__':
    main()
