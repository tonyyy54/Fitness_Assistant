import uuid

import pytest
from fastapi.testclient import TestClient

VALID_PROFILE: dict[str, object] = {
    "biological_sex": "male",
    "birth_date": "1995-06-15",
    "height_cm": 175,
    "current_weight_kg": 80,
    "activity_level": "moderately_active",
}


def authenticated_headers(client: TestClient) -> dict[str, str]:
    """注册并登录一个测试用户，返回认证请求头。"""

    email = f"profile-{uuid.uuid4()}@example.com"
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

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def test_profile_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/profile")

    assert response.status_code == 401


def test_read_profile_returns_not_found_before_creation(
    client: TestClient,
) -> None:
    headers = authenticated_headers(client)

    response = client.get(
        "/api/v1/profile",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User profile not found"


def test_create_profile(
    client: TestClient,
) -> None:
    headers = authenticated_headers(client)

    response = client.put(
        "/api/v1/profile",
        json=VALID_PROFILE,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["biological_sex"] == "male"
    assert response.json()["birth_date"] == "1995-06-15"
    assert response.json()["height_cm"] == 175
    assert response.json()["current_weight_kg"] == 80
    assert response.json()["activity_level"] == "moderately_active"
    assert response.json()["id"]
    assert response.json()["user_id"]


def test_read_created_profile(
    client: TestClient,
) -> None:
    headers = authenticated_headers(client)

    create_response = client.put(
        "/api/v1/profile",
        json=VALID_PROFILE,
        headers=headers,
    )
    assert create_response.status_code == 200

    response = client.get(
        "/api/v1/profile",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == create_response.json()["id"]
    assert response.json()["current_weight_kg"] == 80


def test_update_existing_profile(
    client: TestClient,
) -> None:
    headers = authenticated_headers(client)

    create_response = client.put(
        "/api/v1/profile",
        json=VALID_PROFILE,
        headers=headers,
    )
    assert create_response.status_code == 200

    updated_profile = {
        **VALID_PROFILE,
        "current_weight_kg": 76.5,
        "activity_level": "very_active",
    }

    update_response = client.put(
        "/api/v1/profile",
        json=updated_profile,
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["id"] == create_response.json()["id"]
    assert update_response.json()["current_weight_kg"] == 76.5
    assert update_response.json()["activity_level"] == "very_active"


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("biological_sex", "invalid"),
        ("birth_date", "2999-01-01"),
        ("height_cm", 49),
        ("current_weight_kg", 501),
        ("activity_level", "sometimes"),
    ],
)
def test_profile_rejects_invalid_data(
    client: TestClient,
    field: str,
    invalid_value: object,
) -> None:
    headers = authenticated_headers(client)
    invalid_profile = {
        **VALID_PROFILE,
        field: invalid_value,
    }

    response = client.put(
        "/api/v1/profile",
        json=invalid_profile,
        headers=headers,
    )

    assert response.status_code == 422
