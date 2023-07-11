from fastapi import Depends
from scrap_data.scrap_main import ScrapDataProduct
from sqlalchemy import select, delete, insert, exists
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from price_monitoring.models import Product, Price, product_tb, price_tb
from price_monitoring.schemas import PricesSchema, ProductsSchema


async def checking_product(url: str,
                           session: AsyncSession = Depends(get_async_session)):
    """Проверка товара на мониторинге."""
    query = select(product_tb).where(product_tb.c.url == url)
    result = await session.execute(query)
    return result.all()


async def get_add_product(url: str,
                          session: AsyncSession = Depends(get_async_session)):
    """Добавление товара на мониторинг."""
    res_dict = ScrapDataProduct(url=url).scrap()
    stmt = insert(Product).values(url=url, **res_dict)
    await session.execute(stmt)
    await session.commit()


async def get_all_products(session: AsyncSession = Depends(get_async_session)
                           ) -> list[ProductsSchema]:
    """Показать все продукты на мониторинге."""
    query = select(product_tb)
    result = await session.execute(query)
    return result.all()


async def get_prices_product(
        product_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> list[PricesSchema]:
    """Показать историю цен на продукт."""
    query = select(price_tb).where(price_tb.c.product_id == product_id)
    result = await session.execute(query)
    return result.all()


async def delete_product_from_monitoring(
        product_id: int,
        session: AsyncSession = Depends(get_async_session)):
    stmt = delete(Product).filter(Product.id == product_id)
    await session.execute(stmt)
    await session.commit()
