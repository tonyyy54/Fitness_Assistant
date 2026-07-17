from datetime import date
from decimal import Decimal

import pytest

from app.models.user_profile import UserProfile
from app.models.weight_plan import WeightPlan
from app.services.plan_service import (
    InvalidWeightPlanError,
    calculate_weight_plan,
    validate_weight_plan,
)


def make_profile() -> UserProfile:
    return UserProfile(
        biological_sex="male",
        birth_date=date(1990, 1, 1),
        height_cm=Decimal("175"),
        current_weight_kg=Decimal("80"),
        activity_level="moderately_active",
    )


def test_calculate_weight_plan() -> None:
    plan = WeightPlan(
        target_weight_kg=Decimal("70"),
        weekly_loss_kg=Decimal("0.50"),
    )

    result = calculate_weight_plan(make_profile(), plan)

    assert result.current_weight_kg == 80
    assert result.target_bmi == 22.9
    assert result.daily_calorie_deficit == 550
    assert result.recommended_daily_calories > 1200
    assert result.estimated_weeks == 20
    assert result.warning is None


def test_reject_target_above_current_weight() -> None:
    with pytest.raises(
        InvalidWeightPlanError,
        match="lower than current weight",
    ):
        validate_weight_plan(
            make_profile(),
            target_weight_kg=85,
        )


def test_reject_underweight_target() -> None:
    with pytest.raises(
        InvalidWeightPlanError,
        match="BMI below 18.5",
    ):
        validate_weight_plan(
            make_profile(),
            target_weight_kg=50,
        )
