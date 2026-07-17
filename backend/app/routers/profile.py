from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.dependencies import CurrentUser, DatabaseSession
from app.models.user_profile import UserProfile
from app.schemas.user_profile import (
    UserProfileResponse,
    UserProfileUpsert,
)

router = APIRouter(
    prefix="/api/v1/profile",
    tags=["profile"],
)


@router.get("", response_model=UserProfileResponse)
def read_profile(
    current_user: CurrentUser,
    database_session: DatabaseSession,
) -> UserProfileResponse:
    """获取当前用户的身体档案。"""

    profile = database_session.scalar(
        select(UserProfile).where(
            UserProfile.user_id == current_user.id,
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return UserProfileResponse.model_validate(profile)


@router.put("", response_model=UserProfileResponse)
def upsert_profile(
    profile_data: UserProfileUpsert,
    current_user: CurrentUser,
    database_session: DatabaseSession,
) -> UserProfileResponse:
    """创建或修改当前用户的身体档案。"""

    profile = database_session.scalar(
        select(UserProfile).where(
            UserProfile.user_id == current_user.id,
        )
    )

    if profile is None:
        profile = UserProfile(
            user_id=current_user.id,
            **profile_data.model_dump(),
        )
        database_session.add(profile)
    else:
        for field, value in profile_data.model_dump().items():
            setattr(profile, field, value)

    database_session.commit()
    database_session.refresh(profile)

    return UserProfileResponse.model_validate(profile)
