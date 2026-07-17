import uuid
from datetime import date

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.dependencies import CurrentUser, DatabaseSession
from app.models.user_profile import UserProfile
from app.schemas.user_profile import (
    BodyMetricsResponse,
    UserProfileResponse,
    UserProfileUpsert,
)
from app.services.calorie_service import calculate_body_metrics
from app.services.weight_service import upsert_weight_entry

router = APIRouter(
    prefix="/api/v1/profile",
    tags=["profile"],
)


def find_profile(
    user_id: uuid.UUID,
    database_session: DatabaseSession,
) -> UserProfile | None:
    """根据用户 ID 查询身体档案。"""

    return database_session.scalar(
        select(UserProfile).where(
            UserProfile.user_id == user_id,
        )
    )


@router.get("", response_model=UserProfileResponse)
def read_profile(
    current_user: CurrentUser,
    database_session: DatabaseSession,
) -> UserProfileResponse:
    """获取当前用户的身体档案。"""

    profile = find_profile(current_user.id, database_session)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return UserProfileResponse.model_validate(profile)


@router.get("/metrics", response_model=BodyMetricsResponse)
def read_body_metrics(
    current_user: CurrentUser,
    database_session: DatabaseSession,
) -> BodyMetricsResponse:
    """计算当前用户的 BMI、BMR 与维持热量。"""

    profile = find_profile(current_user.id, database_session)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return BodyMetricsResponse.model_validate(
        calculate_body_metrics(profile),
    )


@router.put("", response_model=UserProfileResponse)
def upsert_profile(
    profile_data: UserProfileUpsert,
    current_user: CurrentUser,
    database_session: DatabaseSession,
) -> UserProfileResponse:
    """创建或修改当前用户的身体档案。"""

    profile = find_profile(current_user.id, database_session)

    if profile is None:
        profile = UserProfile(
            user_id=current_user.id,
            **profile_data.model_dump(),
        )
        database_session.add(profile)
    else:
        for field, value in profile_data.model_dump().items():
            setattr(profile, field, value)

    upsert_weight_entry(
        database_session,
        user_id=current_user.id,
        recorded_on=date.today(),
        weight_kg=profile_data.current_weight_kg,
    )
    database_session.commit()
    database_session.refresh(profile)

    return UserProfileResponse.model_validate(profile)
