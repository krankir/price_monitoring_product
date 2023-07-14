from pydantic import BaseModel


class Item(BaseModel):
    modelName: str
    description: str = 'Описание отсутствует'
    rating: dict[str, float]
