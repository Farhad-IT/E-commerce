from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BalanceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    amount: float
    created_at: datetime


class BalanceCreateSchema(BaseModel):
    amount: float = Field(gt=0)


class BalanceUpdateSchema(BaseModel):
    amount: Optional[float] = Field(gt=0)
