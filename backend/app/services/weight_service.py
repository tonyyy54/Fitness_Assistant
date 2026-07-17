import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.weight_entry import WeightEntry


def find_weight_entry(
    database_session: Session,
    *,
    user_id: uuid.UUID,
    recorded_on: date,
) -> WeightEntry | None:
    return database_session.scalar(
        select(WeightEntry).where(
            WeightEntry.user_id == user_id,
            WeightEntry.recorded_on == recorded_on,
        )
    )


def upsert_weight_entry(
    database_session: Session,
    *,
    user_id: uuid.UUID,
    recorded_on: date,
    weight_kg: float,
    note: str | None = None,
) -> WeightEntry:
    """创建记录；同一天已存在时更新原记录。"""

    entry = find_weight_entry(
        database_session,
        user_id=user_id,
        recorded_on=recorded_on,
    )

    if entry is None:
        entry = WeightEntry(
            user_id=user_id,
            recorded_on=recorded_on,
            weight_kg=weight_kg,
            note=note,
        )
        database_session.add(entry)
    else:
        entry.weight_kg = weight_kg
        entry.note = note

    return entry
