from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel


class ProductsSchema(BaseModel):

    id: int
    url: str
    name: str
    description: str
    rating: float


class PricesSchema(BaseModel):
    price: int
    price_at: Optional[datetime] = None


class ServerResponse(BaseModel):
    error: bool = False
    message: str = 'success'
    payload: Union[list, None] = None
