import uuid

import pytest
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate
from app.services.auth_service import (
    EmailAlreadyRegisteredError,
    authenticate_user,
    create_user,
    get_user_by_email,
)
from app.utils.security import verify_password


def make_email() -> str:
    return f"user-{uuid.uuid4()}@example.com"


def test_create_user_normalizes_email_and_hashes_password(
    database_session: Session,
) -> None:
    password = "a-secure-password"

    user = create_user(
        database_session,
        UserCreate(
            email=f"New-{uuid.uuid4()}@Example.COM",
            password=password,
        ),
    )

    assert user.email == user.email.lower()
    assert user.password_hash != password
    assert verify_password(password, user.password_hash) is True


def test_get_user_by_email_returns_created_user(
    database_session: Session,
) -> None:
    email = make_email()

    created_user = create_user(
        database_session,
        UserCreate(
            email=email,
            password="a-secure-password",
        ),
    )

    found_user = get_user_by_email(database_session, email)

    assert found_user is not None
    assert found_user.id == created_user.id


def test_create_user_rejects_duplicate_email(
    database_session: Session,
) -> None:
    email = make_email()
    user_data = UserCreate(
        email=email,
        password="a-secure-password",
    )

    create_user(database_session, user_data)

    with pytest.raises(EmailAlreadyRegisteredError):
        create_user(database_session, user_data)


def test_authenticate_user_accepts_correct_credentials(
    database_session: Session,
) -> None:
    email = make_email()
    password = "a-secure-password"

    created_user = create_user(
        database_session,
        UserCreate(
            email=email,
            password=password,
        ),
    )

    authenticated_user = authenticate_user(
        database_session,
        email,
        password,
    )

    assert authenticated_user is not None
    assert authenticated_user.id == created_user.id


def test_authenticate_user_rejects_wrong_password(
    database_session: Session,
) -> None:
    email = make_email()

    create_user(
        database_session,
        UserCreate(
            email=email,
            password="a-secure-password",
        ),
    )

    authenticated_user = authenticate_user(
        database_session,
        email,
        "wrong-password",
    )

    assert authenticated_user is None


def test_authenticate_user_rejects_unknown_email(
    database_session: Session,
) -> None:
    authenticated_user = authenticate_user(
        database_session,
        make_email(),
        "a-secure-password",
    )

    assert authenticated_user is None
