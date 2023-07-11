from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from price_monitoring import service
from price_monitoring.schemas import (
    ProductsSchema, PricesSchema, ServerResponse,
)

router = APIRouter(
    prefix='/monitoring',
    tags=['Monitoring price']
)


@router.post('/add/', response_model=ServerResponse)
async def add_product(
        url: str, session: AsyncSession = Depends(get_async_session)):
    """Добавление нового товара на мониторинг."""
    if not await service.checking_product(url, session):
        await service.get_add_product(url, session)
        return {
            'error': False,
            'message': 'success add product',
            'payload': None,
        }
    return {
            'error': True,
            'message': 'this product has already been added',
            'payload': None,
        }


@router.get("/all_products", response_model=ServerResponse)
async def get_biggest_cities(
        session: AsyncSession = Depends(get_async_session)):
    """Получение всех товаров находящихся на мониторинге."""
    products = await service.get_all_products(session)
    result = [ProductsSchema(id=product.id,
                             url=product.url,
                             name=product.name,
                             description=product.description,
                             rating=product.rating) for product in products]
    return {
        'error': False,
        'message': 'success',
        'payload': result,
    }


@router.get('/product_prices', response_model=ServerResponse)
async def product_price(
        product_id: int,
        session: AsyncSession = Depends(get_async_session), ):
    """Получение истории цен на товар."""
    prices = await service.get_prices_product(product_id, session)
    result = [PricesSchema(price=price.price, price_at=price.price_at) for price
              in prices]
    return {
        'error': False,
        'message': 'success',
        'payload': result,
    }


@router.delete('/delete', response_model=ServerResponse)
async def del_product(
        product_id: int, session: AsyncSession = Depends(get_async_session)):
    """Удаление товара из мониторинга."""
    await service.delete_product_from_monitoring(product_id, session)
    return {
        'error': False,
        'message': 'product delete',
        'payload': None,
    }
