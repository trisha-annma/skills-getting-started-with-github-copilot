import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Soccer Team" in data


def test_signup_adds_participant(client):
    activity_name = "Soccer Team"
    email = "new.student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Soccer Team"
    email = "liam@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown Activity/signup", params={"email": "new@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    activity_name = "Soccer Team"
    email = "liam@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant_returns_404(client):
    response = client.delete(
        "/activities/Soccer Team/unregister",
        params={"email": "not.registered@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_unregister_unknown_activity_returns_404(client):
    response = client.delete("/activities/Unknown Activity/unregister", params={"email": "new@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
