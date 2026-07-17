import uuid

from fastapi.testclient import TestClient

from app.utils.security import create_access_token


def register_and_login(
    client: TestClient,
) -> tuple[str, str, str]:
    email = f"user-{uuid.uuid4()}@example.com"
    password = "a-secure-password"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200

    return (
        register_response.json()["id"],
        email,
        login_response.json()["access_token"],
    )


def test_read_current_user_returns_authenticated_user(
    client: TestClient,
) -> None:
    user_id, email, token = register_and_login(client)

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["email"] == email
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_read_current_user_rejects_missing_token(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_read_current_user_rejects_invalid_token(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_read_current_user_rejects_unknown_user(
    client: TestClient,
) -> None:
    token = create_access_token(str(uuid.uuid4()))

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
