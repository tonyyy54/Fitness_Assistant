from datetime import date

import pytest

from app.services.calorie_service import (
    calculate_age,
    calculate_bmi,
    calculate_bmr,
)


def test_calculate_age_before_birthday() -> None:
    age = calculate_age(
        date(1995, 8, 20),
        today=date(2026, 7, 17),
    )

    assert age == 30


def test_calculate_age_after_birthday() -> None:
    age = calculate_age(
        date(1995, 6, 15),
        today=date(2026, 7, 17),
    )

    assert age == 31


def test_calculate_bmi() -> None:
    assert calculate_bmi(weight_kg=80, height_cm=175) == 26.1


@pytest.mark.parametrize(
    ("biological_sex", "expected_bmr"),
    [
        ("male", 1748.75),
        ("female", 1582.75),
    ],
)
def test_calculate_bmr(
    biological_sex: str,
    expected_bmr: float,
) -> None:
    bmr = calculate_bmr(
        biological_sex=biological_sex,
        age=30,
        height_cm=175,
        weight_kg=80,
    )

    assert bmr == expected_bmr
