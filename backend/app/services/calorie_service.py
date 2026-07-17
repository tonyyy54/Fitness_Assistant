from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.models.user_profile import UserProfile

ACTIVITY_FACTORS: dict[str, float] = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9,
}


@dataclass(frozen=True)
class BodyMetrics:
    """由身体档案计算出的健康指标。"""

    age: int
    bmi: float
    bmr_kcal: int
    maintenance_calories_kcal: int


def calculate_age(
    birth_date: date,
    *,
    today: date | None = None,
) -> int:
    """根据生日计算完整周岁。"""

    reference_date = today or date.today()

    return (
        reference_date.year
        - birth_date.year
        - (
            (reference_date.month, reference_date.day)
            < (birth_date.month, birth_date.day)
        )
    )


def calculate_bmi(
    weight_kg: Decimal | float,
    height_cm: Decimal | float,
) -> float:
    """计算 BMI 并保留一位小数。"""

    height_m = float(height_cm) / 100
    return round(float(weight_kg) / height_m**2, 1)


def calculate_bmr(
    *,
    biological_sex: str,
    age: int,
    height_cm: Decimal | float,
    weight_kg: Decimal | float,
) -> float:
    """使用 Mifflin-St Jeor 公式计算基础代谢。"""

    base = 10 * float(weight_kg) + 6.25 * float(height_cm) - 5 * age

    if biological_sex == "male":
        return base + 5

    if biological_sex == "female":
        return base - 161

    raise ValueError("Unsupported biological sex")


def calculate_body_metrics(
    profile: UserProfile,
    *,
    today: date | None = None,
) -> BodyMetrics:
    """根据用户身体档案生成首页健康指标。"""

    age = calculate_age(profile.birth_date, today=today)
    bmr = calculate_bmr(
        biological_sex=profile.biological_sex,
        age=age,
        height_cm=profile.height_cm,
        weight_kg=profile.current_weight_kg,
    )
    activity_factor = ACTIVITY_FACTORS[profile.activity_level]

    return BodyMetrics(
        age=age,
        bmi=calculate_bmi(
            profile.current_weight_kg,
            profile.height_cm,
        ),
        bmr_kcal=round(bmr),
        maintenance_calories_kcal=round(bmr * activity_factor),
    )
