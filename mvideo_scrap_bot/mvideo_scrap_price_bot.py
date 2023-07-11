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
import psycopg2 as ps
from aiogram.utils.markdown import hbold, hlink

from config import DATABASE_URI
from scrap_data.scrap_main import ScrapDataProduct

load_dotenv()

base = ps.connect(DATABASE_URI)
base.autocommit = True
cur = base.cursor()

bot = Bot(token=os.getenv('TOKEN'), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

PRODUCT_LINC = ''
NAME_PRODUCT_DELETE = ''
NAME_PRODUCT_PRICE = ''


async def on_startup(_):
    print('Бот вышел в онлайн...')


async def on_shutdown(_):
    print('Закрываю соединение с БД')
    cur.close()
    base.close()


b1 = KeyboardButton('Получение списка всех товаров')
b2 = KeyboardButton('Удаление товара')
b3 = KeyboardButton('Добавить товар на мониторинг')
b4 = KeyboardButton('Получение истории цен на товар')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.row(b1, b2).add(b3).add(b4)


@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    await message.answer(f'Добрый день {message.from_user.first_name}! '
                         f'Для добавления товара на мониторинг, напишите ссылку на товар.'
                         f'Или воспользуйтесь меню ⬇',
                         reply_markup=kb_client,
                         )


price_product = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(
    text='Да, показать цену этого товара', callback_data='get_price'))


@dp.message_handler(
    lambda message: 'Получение истории цен на товар' in message.text)
async def delete_product(message: types.Message):
    """История изменения цен на товар."""
    await message.answer('Напишите в чат: история цен (название товара)')


@dp.message_handler(lambda message: 'история цен' in message.text.lower())
async def delete_product(message: types.Message):
    """История изменения цен на товар."""
    global NAME_PRODUCT_PRICE
    NAME_PRODUCT_PRICE = message.text[11:].strip()
    await message.answer(
        f'Показать цену именно этого товара? {NAME_PRODUCT_PRICE}',
        reply_markup=price_product,
    )


@dp.callback_query_handler(text='get_price')
async def get_price_product(callback: types.CallbackQuery):
    """История изменения цен на товар."""
    await callback.answer('Показать цены на товар')
    exists_query = """SELECT EXISTS (SELECT products.name FROM products WHERE name = %s)"""
    cur.execute(exists_query, (NAME_PRODUCT_PRICE,))
    if not cur.fetchone()[0]:
        await callback.message.answer(
            '❌Товара с таким названием ещё нету в списке, сначала добавьте товар')
    else:
        cur.execute(
            f"""select prices.price, prices.price_at from products join prices on products.id = prices.product_id where products.name = '{NAME_PRODUCT_PRICE}'""")
        for index, product in enumerate(cur):
            times = product[1].strftime('%Y.%d.%m %H:%M')
            card = f'{hbold("Товар: ")} {NAME_PRODUCT_PRICE}\n' \
                   f'{hbold("Цена: ")} {product[0]}🔥\n' \
                   f'{hbold("Дата и время обновления: ")} {times}\n'

            #  Защита от бана за флуд.
            if index % 20 == 0:
                time.sleep(3)

            await callback.message.answer(card)


@dp.message_handler(
    lambda message: 'Получение списка всех товаров' in message.text)
async def all_product(message: types.Message):
    """Просмотр всех товаров на мониторинге."""
    await message.answer('Пожалуйста подождите⌛...')
    cur.execute(
        """SELECT * FROM products"""
    )
    for index, product in enumerate(cur):
        linc = hlink(product[2], product[1])
        card = f'{hbold("Ссылка: ")} {linc}\n' \
               f'{hbold("Рейтинг: ")} {product[4]}🔥\n' \
               f'{hbold("Название: ")} {product[2]}\n' \
               f'{hbold("Описание: ")} {product[3]}\n'

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
                         ' удалить (полное название товара из карточки)')


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
    await callback.answer('Начать удаление?', show_alert=True)
    cur.execute("DELETE FROM products WHERE name = %s",
                (NAME_PRODUCT_DELETE,))
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
    exists_query = """SELECT EXISTS (SELECT products.url FROM products WHERE url = %s)"""
    cur.execute(exists_query, (linc,))
    if cur.fetchone()[0]:
        await callback.message.answer('❌Товар уже был добавлен ранее')
    else:
        cur.execute(
            """INSERT INTO products (url, name, description, rating) VALUES (%s, %s, %s, %s);""",
            (linc, name, description, rating))
        await callback.message.answer('Товар успешно добавлен✅')


@dp.message_handler()
async def echo_send(message: types.Message):
    """Эхо обработчик."""
    await message.reply(
        'Неверная команда, прочтите ещё раз какой должен быть запрос и повтрите'
        ' попытку...')


def main():
    executor.start_polling(dp, skip_updates=True,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown,
                           )


if __name__ == '__main__':
    main()
