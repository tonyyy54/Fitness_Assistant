import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class WeightPlanUpsert(BaseModel):
    """创建或修改减重目标时提交的数据。"""

    target_weight_kg: float = Field(ge=20, le=500)
    weekly_loss_kg: float = Field(ge=0.25, le=0.9)


class WeightPlanResponse(BaseModel):
    """减重目标及根据身体档案生成的实时建议。"""

    id: uuid.UUID
    user_id: uuid.UUID
    target_weight_kg: float
    weekly_loss_kg: float
    current_weight_kg: float
    target_bmi: float
    daily_calorie_deficit: int
    recommended_daily_calories: int
    estimated_weeks: int
    warning: str | None
    created_at: datetime
    updated_at: datetime
