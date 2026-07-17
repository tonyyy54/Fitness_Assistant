from datetime import timedelta

import pytest
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_return_plain_password() -> None:
    password = "a-secure-password"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password.startswith("$argon2")


def test_verify_password_accepts_correct_password() -> None:
    password = "a-secure-password"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_verify_password_rejects_incorrect_password() -> None:
    hashed_password = hash_password("a-secure-password")

    assert verify_password("wrong-password", hashed_password) is False


def test_same_password_produces_different_hashes() -> None:
    password = "a-secure-password"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash


def test_access_token_can_be_decoded() -> None:
    token = create_access_token("user-id")

    assert decode_access_token(token) == "user-id"


def test_access_token_rejects_tampering() -> None:
    token = create_access_token("user-id")
    tampered_token = f"{token}invalid"

    with pytest.raises(InvalidTokenError):
        decode_access_token(tampered_token)


def test_access_token_rejects_expired_token() -> None:
    token = create_access_token(
        "user-id",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token)
