from pydantic import BaseModel


class Item(BaseModel):
    modelName: str
    description: str
    rating: dict[str, float]
