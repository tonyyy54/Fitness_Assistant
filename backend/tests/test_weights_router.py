import uuid
from datetime import date, timedelta

from fastapi.testclient import TestClient

PROFILE_DATA: dict[str, object] = {
    "biological_sex": "male",
    "birth_date": "1990-01-01",
    "height_cm": 175,
    "current_weight_kg": 80,
    "activity_level": "moderately_active",
}


def authenticated_headers(client: TestClient) -> dict[str, str]:
    email = f"weight-{uuid.uuid4()}@example.com"
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


def test_weight_history_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/weights")

    assert response.status_code == 401


def test_weight_entry_requires_profile(client: TestClient) -> None:
    headers = authenticated_headers(client)

    response = client.put(
        "/api/v1/weights",
        json={
            "recorded_on": date.today().isoformat(),
            "weight_kg": 79.5,
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User profile not found"


def test_profile_creation_adds_initial_weight_entry(
    client: TestClient,
) -> None:
    headers = authenticated_headers(client)
    create_profile(client, headers)

    response = client.get(
        "/api/v1/weights",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["weight_kg"] == 80
    assert response.json()[0]["recorded_on"] == date.today().isoformat()


def test_update_today_weight_syncs_profile(
    client: TestClient,
) -> None:
    headers = authenticated_headers(client)
    create_profile(client, headers)

    history_response = client.get(
        "/api/v1/weights",
        headers=headers,
    )
    original_id = history_response.json()[0]["id"]

    update_response = client.put(
        "/api/v1/weights",
        json={
            "recorded_on": date.today().isoformat(),
            "weight_kg": 79.5,
            "note": "Morning measurement",
        },
        headers=headers,
    )
    profile_response = client.get(
        "/api/v1/profile",
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["id"] == original_id
    assert update_response.json()["weight_kg"] == 79.5
    assert profile_response.json()["current_weight_kg"] == 79.5


def test_weight_history_is_chronological(
    client: TestClient,
) -> None:
    headers = authenticated_headers(client)
    create_profile(client, headers)

    for days_ago, weight in [(2, 80.8), (1, 80.3)]:
        response = client.put(
            "/api/v1/weights",
            json={
                "recorded_on": (date.today() - timedelta(days=days_ago)).isoformat(),
                "weight_kg": weight,
            },
            headers=headers,
        )
        assert response.status_code == 200

    response = client.get(
        "/api/v1/weights",
        headers=headers,
    )

    weights = [entry["weight_kg"] for entry in response.json()]
    assert weights == [80.8, 80.3, 80]


def test_reject_future_weight_date(client: TestClient) -> None:
    headers = authenticated_headers(client)
    create_profile(client, headers)

    response = client.put(
        "/api/v1/weights",
        json={
            "recorded_on": (date.today() + timedelta(days=1)).isoformat(),
            "weight_kg": 79,
        },
        headers=headers,
    )

    assert response.status_code == 422
