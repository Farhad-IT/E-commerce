from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class CategoryCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=50)
