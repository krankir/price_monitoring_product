from pydantic import BaseModel, root_validator


class Item(BaseModel):
    modelName: str
    description: str
    rating: dict[str, float]
