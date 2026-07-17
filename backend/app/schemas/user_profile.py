import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

BiologicalSex = Literal["male", "female"]

ActivityLevel = Literal[
    "sedentary",
    "lightly_active",
    "moderately_active",
    "very_active",
    "extra_active",
]


class UserProfileUpsert(BaseModel):
    """创建或修改身体档案时提交的数据。"""

    biological_sex: BiologicalSex
    birth_date: date
    height_cm: float = Field(ge=50, le=300)
    current_weight_kg: float = Field(ge=20, le=500)
    activity_level: ActivityLevel

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Birth date must be in the past")

        return value


class UserProfileResponse(BaseModel):
    """返回给客户端的身体档案。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    biological_sex: BiologicalSex
    birth_date: date
    height_cm: float
    current_weight_kg: float
    activity_level: ActivityLevel
    created_at: datetime
    updated_at: datetime
