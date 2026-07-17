import uuid
from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class WeightEntryUpsert(BaseModel):
    """新增或修改某一天的体重记录。"""

    weight_kg: float = Field(ge=20, le=500)
    recorded_on: date
    note: str | None = Field(default=None, max_length=500)

    @field_validator("recorded_on")
    @classmethod
    def validate_recorded_on(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Weight date cannot be in the future")

        return value


class WeightEntryResponse(BaseModel):
    """返回给客户端的体重记录。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    weight_kg: float
    recorded_on: date
    note: str | None
    created_at: datetime
    updated_at: datetime
