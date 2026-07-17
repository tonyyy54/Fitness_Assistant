import uuid

from fastapi.testclient import TestClient

PROFILE_DATA: dict[str, object] = {
    "biological_sex": "male",
    "birth_date": "1990-01-01",
    "height_cm": 175,
    "current_weight_kg": 80,
    "activity_level": "moderately_active",
}

PLAN_DATA: dict[str, object] = {
    "target_weight_kg": 70,
    "weekly_loss_kg": 0.5,
}


def authenticated_headers(client: TestClient) -> dict[str, str]:
    email = f"plan-{uuid.uuid4()}@example.com"
    password = "a-secure-password"

    client.post(
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

    return {
        "Authorization": (f"Bearer {login_response.json()['access_token']}"),
    }


def create_profile(
    client: TestClient,
    headers: dict[str, str],
) -> None:
    response = client.put(
        "/api/v1/profile",
        json=PROFILE_DATA,
        headers=headers,
    )
    assert response.status_code == 200


def test_plan_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/plan")

    assert response.status_code == 401


def test_plan_requires_profile(client: TestClient) -> None:
    headers = authenticated_headers(client)

    response = client.put(
        "/api/v1/plan",
        json=PLAN_DATA,
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User profile not found"


def test_read_missing_plan(client: TestClient) -> None:
    headers = authenticated_headers(client)
    create_profile(client, headers)

    response = client.get(
        "/api/v1/plan",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Weight plan not found"


def test_create_weight_plan(client: TestClient) -> None:
    headers = authenticated_headers(client)
    create_profile(client, headers)

    response = client.put(
        "/api/v1/plan",
        json=PLAN_DATA,
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["target_weight_kg"] == 70
    assert response.json()["weekly_loss_kg"] == 0.5
    assert response.json()["current_weight_kg"] == 80
    assert response.json()["target_bmi"] == 22.9
    assert response.json()["daily_calorie_deficit"] == 550
    assert response.json()["estimated_weeks"] == 20


def test_update_weight_plan_keeps_same_id(client: TestClient) -> None:
    headers = authenticated_headers(client)
    create_profile(client, headers)

    first_response = client.put(
        "/api/v1/plan",
        json=PLAN_DATA,
        headers=headers,
    )
    update_response = client.put(
        "/api/v1/plan",
        json={
            "target_weight_kg": 72,
            "weekly_loss_kg": 0.25,
        },
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["id"] == first_response.json()["id"]
    assert update_response.json()["target_weight_kg"] == 72
    assert update_response.json()["estimated_weeks"] == 32


def test_reject_target_above_current_weight(client: TestClient) -> None:
    headers = authenticated_headers(client)
    create_profile(client, headers)

    response = client.put(
        "/api/v1/plan",
        json={
            "target_weight_kg": 85,
            "weekly_loss_kg": 0.5,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert "lower than current weight" in response.json()["detail"]


def test_reject_weekly_loss_above_limit(client: TestClient) -> None:
    headers = authenticated_headers(client)
    create_profile(client, headers)

    response = client.put(
        "/api/v1/plan",
        json={
            "target_weight_kg": 70,
            "weekly_loss_kg": 1.5,
        },
        headers=headers,
    )

    assert response.status_code == 422
