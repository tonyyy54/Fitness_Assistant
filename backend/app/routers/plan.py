import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.dependencies import CurrentUser, DatabaseSession
from app.models.user_profile import UserProfile
from app.models.weight_plan import WeightPlan
from app.schemas.weight_plan import (
    WeightPlanResponse,
    WeightPlanUpsert,
)
from app.services.plan_service import (
    InvalidWeightPlanError,
    calculate_weight_plan,
    validate_weight_plan,
)

router = APIRouter(
    prefix="/api/v1/plan",
    tags=["plan"],
)


def find_profile(
    user_id: uuid.UUID,
    database_session: DatabaseSession,
) -> UserProfile | None:
    return database_session.scalar(
        select(UserProfile).where(
            UserProfile.user_id == user_id,
        )
    )


def find_plan(
    user_id: uuid.UUID,
    database_session: DatabaseSession,
) -> WeightPlan | None:
    return database_session.scalar(
        select(WeightPlan).where(
            WeightPlan.user_id == user_id,
        )
    )


def build_plan_response(
    profile: UserProfile,
    plan: WeightPlan,
) -> WeightPlanResponse:
    metrics = calculate_weight_plan(profile, plan)

    return WeightPlanResponse(
        id=plan.id,
        user_id=plan.user_id,
        target_weight_kg=float(plan.target_weight_kg),
        weekly_loss_kg=float(plan.weekly_loss_kg),
        current_weight_kg=metrics.current_weight_kg,
        target_bmi=metrics.target_bmi,
        daily_calorie_deficit=metrics.daily_calorie_deficit,
        recommended_daily_calories=metrics.recommended_daily_calories,
        estimated_weeks=metrics.estimated_weeks,
        warning=metrics.warning,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.get("", response_model=WeightPlanResponse)
def read_weight_plan(
    current_user: CurrentUser,
    database_session: DatabaseSession,
) -> WeightPlanResponse:
    """读取当前用户的减重目标。"""

    profile = find_profile(current_user.id, database_session)
    plan = find_plan(current_user.id, database_session)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weight plan not found",
        )

    return build_plan_response(profile, plan)


@router.put("", response_model=WeightPlanResponse)
def upsert_weight_plan(
    plan_data: WeightPlanUpsert,
    current_user: CurrentUser,
    database_session: DatabaseSession,
) -> WeightPlanResponse:
    """创建或修改当前用户的减重目标。"""

    profile = find_profile(current_user.id, database_session)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    try:
        validate_weight_plan(
            profile,
            target_weight_kg=plan_data.target_weight_kg,
        )
    except InvalidWeightPlanError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    plan = find_plan(current_user.id, database_session)

    if plan is None:
        plan = WeightPlan(
            user_id=current_user.id,
            **plan_data.model_dump(),
        )
        database_session.add(plan)
    else:
        plan.target_weight_kg = plan_data.target_weight_kg
        plan.weekly_loss_kg = plan_data.weekly_loss_kg

    database_session.commit()
    database_session.refresh(plan)

    return build_plan_response(profile, plan)
