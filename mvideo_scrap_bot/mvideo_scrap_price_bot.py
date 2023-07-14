import asyncio
import os
import time

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.markdown import hbold, hlink
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlalchemy import desc, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from models import Product, Price
from config import DATABASE_URI
from scrap_data.scrap_main import ScrapDataProduct

load_dotenv()


def create_async_engine(url):
    return _create_async_engine(url=url,
                                echo=True,
                                pool_pre_ping=True,
                                )


def get_session_maker(engine):
    return sessionmaker(engine, class_=AsyncSession)


async_engine = create_async_engine(DATABASE_URI)
session_maker = get_session_maker(async_engine)


async def main():
    bot = Bot(token=os.getenv('TOKEN'), parse_mode=types.ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    class ChoiceLincProduct(StatesGroup):
        product_linc = State()

    class ChoiceIdProductDelete(StatesGroup):
        id_product_delete = State()

    class ChoiceIdProductPrice(StatesGroup):
        id_product_price = State()

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
                             f'Для добавления товара, напишите ссылку'
                             f' на товар.Или воспользуйтесь меню ⬇',
                             reply_markup=kb_client,
                             )

    @dp.message_handler(
        lambda message: 'Получение истории цен на товар' in message.text)
    async def price_product(message: types.Message):
        """История изменения цен на товар."""
        await message.answer('Напишите в чат id товара ')
        await ChoiceIdProductPrice.id_product_price.set()

    @dp.message_handler(state=ChoiceIdProductPrice.id_product_price)
    async def price_history_product(message: types.Message, state: FSMContext):
        """История изменения цен на товар."""
        await state.update_data(id_product_price=message.text)
        data = await state.get_data()
        id_price = int(data.get('id_product_price'))
        async with session_maker() as session:
            async with session.begin():
                session: AsyncSession
                result = await session.execute(
                    select(Product).where(Product.id == id_price)
                )
                product = result.one_or_none()
                if product is None:
                    await message.answer(
                        '❌Товара с таким id ещё нету в списке,'
                        ' сначала добавьте товар')
                    await state.finish()
                else:
                    a = await session.execute(
                        select(Price).filter(
                            Price.product_id == id_price).order_by(
                            desc(Price.price_at))
                    )
                    res = a.scalars()
                    for index, product in enumerate(res):
                        card = f'{hbold("Товар c id: ")} {id_price}\n' \
                               f'{hbold("Цена: ")} {product.price}🔥\n' \
                               f'{hbold("Дата и время обновления: ")}' \
                               f' {product.price_at}\n'

                        if index == 20:
                            break

                        await message.answer(card)
                        await state.finish()

    @dp.message_handler(
        lambda message: 'Получение списка всех товаров' in message.text)
    async def all_product(message: types.Message):
        """Просмотр всех товаров на мониторинге."""
        await message.answer('Пожалуйста подождите⌛...')
        async with session_maker() as session:
            async with session.begin():
                session: AsyncSession
                result = await session.execute(select(Product))
                users = result.scalars().all()
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

    @dp.message_handler(lambda message: 'Удаление товара' in message.text)
    async def delete_product_(message: types.Message):
        """Удаление товара из мониторинга."""
        await message.answer(
            'Напишите id товара из карточки для его удаления из мониторинга'
        )
        await ChoiceIdProductDelete.id_product_delete.set()

    @dp.message_handler(state=ChoiceIdProductDelete.id_product_delete)
    async def delete_product(message: types.Message, state: FSMContext):
        """Удаление товара из мониторинга."""
        await state.update_data(id_product_delete=message.text)
        data = await state.get_data()
        id_p = int(data.get('id_product_delete'))
        async with session_maker() as session:
            async with session.begin():
                session: AsyncSession
                await session.execute(select(Product))
                product_delete = await session.get(Product, id_p)
                await session.delete(product_delete)
                await message.answer('Товар успешно удалён 🗑')
                await state.finish()

    @dp.message_handler(
        lambda message: 'Добавить товар на мониторинг' in message.text)
    async def add_product(message: types.Message):
        """Добавление товара на мониторинг."""
        await message.answer('Напишите ссылку на товар с сайта М.видео')
        await ChoiceLincProduct.product_linc.set()

    @dp.message_handler(state=ChoiceLincProduct.product_linc)
    async def www_par(message: types.Message, state: FSMContext):
        """Добавление товара на мониторинг."""
        if message.text[:31] != 'https://www.mvideo.ru/products/':
            await message.answer('❌ Некорректная ссылка на товар.')
            return
        await state.update_data(product_linc=message.text)
        data = await state.get_data()
        linc = str(data.get('product_linc'))
        product = ScrapDataProduct(linc).scrap()
        name = product['name']
        description = product['description']
        rating = product['rating']
        async with session_maker() as session:
            async with session.begin():
                session: AsyncSession
                res = await session.execute(
                    select(Product).where(Product.url == linc))
                product = res.one_or_none()
                if product is not None:
                    await message.answer(
                        '❌ Данный товар уже присутствует на мониторинге.')
                    await state.finish()
                else:
                    new_product = Product(url=linc,
                                          name=name,
                                          description=description,
                                          rating=rating,
                                          )
                    session.add(new_product)
                    await session.commit()
                    await message.answer('Товар успешно добавлен✅')
                    await state.finish()

    @dp.message_handler()
    async def echo_send(message: types.Message):
        """Эхо обработчик."""
        await message.reply(
            'Неверная команда, прочтите ещё раз какой должен быть запрос и'
            ' повторите попытку...')

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
