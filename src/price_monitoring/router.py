from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from scrap_data.scrap_main import ScrapDataProduct
from database import get_async_session
from .models import Product, Price

router = APIRouter(
    prefix='/monitoring',
    tags=['Monitoring price']
)


@router.post('/add/')
async def add_product(
        url: str, session: AsyncSession = Depends(get_async_session)):
    """Добавление нового товара на мониторинг."""
    res_dict = ScrapDataProduct(url=url).scrap()
    stmt = insert(Product).values(url=url, **res_dict)
    await session.execute(stmt)
    await session.commit()
    return {
        'status': 'success',
    }


@router.delete('/delete')
async def del_product(
        product_id: int, session: AsyncSession = Depends(get_async_session)):
    """Удаление товара из мониторинга."""
    print(type(product_id))
    query = delete(Product).filter(Product.id == product_id)
    print(query)
    await session.execute(query)
    await session.commit()
    return {
        'status': 'product delete'
    }


@router.get('/all_products')
async def all_product(
        session: AsyncSession = Depends(get_async_session)):
    """Получение списка товаров на мониторинге."""
    query = select(Product)
    result = await session.execute(query)
    return result.scalars().all()


@router.get('/product_prices')
async def product_price(
        product_id: int,
        session: AsyncSession = Depends(get_async_session), ):
    """Получение истории цен на товар."""
    query = select(Price).filter(Price.product_id == product_id)
    result = await session.execute(query)
    res = result.scalars().all()
    res_list = []
    for i in res:
        resul = {
            'price': i.price,
            'price_at': i.price_at,
        }
        res_list.append(resul)
    return res_list
