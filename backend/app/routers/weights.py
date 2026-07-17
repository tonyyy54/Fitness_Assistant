from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.dependencies import CurrentUser, DatabaseSession
from app.models.user_profile import UserProfile
from app.models.weight_entry import WeightEntry
from app.schemas.weight_entry import (
    WeightEntryResponse,
    WeightEntryUpsert,
)
from app.services.weight_service import upsert_weight_entry

HistoryLimit = Annotated[int, Query(ge=1, le=365)]

router = APIRouter(
    prefix="/api/v1/weights",
    tags=["weights"],
)


@router.get("", response_model=list[WeightEntryResponse])
def read_weight_entries(
    current_user: CurrentUser,
    database_session: DatabaseSession,
    limit: HistoryLimit = 90,
) -> list[WeightEntryResponse]:
    """按日期升序返回最近的体重记录。"""

    entries = list(
        database_session.scalars(
            select(WeightEntry)
            .where(WeightEntry.user_id == current_user.id)
            .order_by(WeightEntry.recorded_on.desc())
            .limit(limit)
        )
    )
    entries.reverse()

    return [WeightEntryResponse.model_validate(entry) for entry in entries]


@router.put("", response_model=WeightEntryResponse)
def upsert_current_weight(
    entry_data: WeightEntryUpsert,
    current_user: CurrentUser,
    database_session: DatabaseSession,
) -> WeightEntryResponse:
    """保存某一天的体重并同步身体档案中的当前体重。"""

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

    latest_entry = database_session.scalar(
        select(WeightEntry)
        .where(WeightEntry.user_id == current_user.id)
        .order_by(WeightEntry.recorded_on.desc())
        .limit(1)
    )
    entry = upsert_weight_entry(
        database_session,
        user_id=current_user.id,
        recorded_on=entry_data.recorded_on,
        weight_kg=entry_data.weight_kg,
        note=entry_data.note,
    )

    if latest_entry is None or entry_data.recorded_on >= latest_entry.recorded_on:
        profile.current_weight_kg = entry_data.weight_kg

    database_session.commit()
    database_session.refresh(entry)

    return WeightEntryResponse.model_validate(entry)
