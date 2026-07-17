import uuid

from fastapi.testclient import TestClient

from app.utils.security import decode_access_token


def make_email() -> str:
    return f"user-{uuid.uuid4()}@example.com"


def test_register_user_returns_created_user(
    client: TestClient,
) -> None:
    email = make_email()

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "a-secure-password",
        },
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["email"] == email
    assert response_data["is_active"] is True
    assert "id" in response_data
    assert "created_at" in response_data
    assert "password" not in response_data
    assert "password_hash" not in response_data


def test_register_user_rejects_duplicate_email(
    client: TestClient,
) -> None:
    request_data = {
        "email": make_email(),
        "password": "a-secure-password",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=request_data,
    )
    second_response = client.post(
        "/api/v1/auth/register",
        json=request_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Email already registered",
    }


def test_register_user_rejects_invalid_data(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_login_returns_access_token(
    client: TestClient,
) -> None:
    email = make_email()
    password = "a-secure-password"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201
    assert login_response.status_code == 200

    response_data = login_response.json()

    assert response_data["token_type"] == "bearer"
    assert response_data["expires_in"] == 1800
    assert (
        decode_access_token(
            response_data["access_token"],
        )
        == register_response.json()["id"]
    )


def test_login_rejects_wrong_password(
    client: TestClient,
) -> None:
    email = make_email()

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "a-secure-password",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect email or password",
    }
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_rejects_unknown_email(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": make_email(),
            "password": "a-secure-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect email or password",
    }
