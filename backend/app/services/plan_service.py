from dataclasses import dataclass
from math import ceil

from app.models.user_profile import UserProfile
from app.models.weight_plan import WeightPlan
from app.services.calorie_service import (
    calculate_age,
    calculate_bmi,
    calculate_body_metrics,
)

CALORIES_PER_KILOGRAM = 7700
MINIMUM_DAILY_CALORIES = 1200
MINIMUM_TARGET_BMI = 18.5


class InvalidWeightPlanError(ValueError):
    """减重目标不符合业务或安全规则。"""


@dataclass(frozen=True)
class WeightPlanMetrics:
    """根据当前身体档案实时计算的减重计划。"""

    current_weight_kg: float
    target_bmi: float
    daily_calorie_deficit: int
    recommended_daily_calories: int
    estimated_weeks: int
    warning: str | None


def validate_weight_plan(
    profile: UserProfile,
    *,
    target_weight_kg: float,
) -> None:
    """验证目标体重是否适合生成成人减重计划。"""

    if calculate_age(profile.birth_date) < 18:
        raise InvalidWeightPlanError(
            "Weight planning is currently available for adults only",
        )

    if target_weight_kg >= float(profile.current_weight_kg):
        raise InvalidWeightPlanError(
            "Target weight must be lower than current weight",
        )

    target_bmi = calculate_bmi(
        target_weight_kg,
        profile.height_cm,
    )

    if target_bmi < MINIMUM_TARGET_BMI:
        raise InvalidWeightPlanError(
            "Target weight would result in a BMI below 18.5",
        )


def calculate_weight_plan(
    profile: UserProfile,
    plan: WeightPlan,
) -> WeightPlanMetrics:
    """计算每日热量缺口、建议摄入量与预计周数。"""

    current_weight = float(profile.current_weight_kg)
    target_weight = float(plan.target_weight_kg)
    weekly_loss = float(plan.weekly_loss_kg)
    body_metrics = calculate_body_metrics(profile)
    requested_deficit = round(
        weekly_loss * CALORIES_PER_KILOGRAM / 7,
    )
    calculated_calories = body_metrics.maintenance_calories_kcal - requested_deficit
    warning = None

    if calculated_calories < MINIMUM_DAILY_CALORIES:
        calculated_calories = MINIMUM_DAILY_CALORIES
        warning = (
            "The requested pace would require a very low calorie intake. "
            "The recommendation was limited to 1200 kcal; consult a "
            "qualified health professional."
        )

    return WeightPlanMetrics(
        current_weight_kg=current_weight,
        target_bmi=calculate_bmi(
            target_weight,
            profile.height_cm,
        ),
        daily_calorie_deficit=requested_deficit,
        recommended_daily_calories=calculated_calories,
        estimated_weeks=ceil(
            (current_weight - target_weight) / weekly_loss,
        ),
        warning=warning,
    )
