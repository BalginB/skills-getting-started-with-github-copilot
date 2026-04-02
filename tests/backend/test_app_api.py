import copy

from fastapi.testclient import TestClient

from src.app import app, activities as activities_data

ORIGINAL_ACTIVITIES = copy.deepcopy(activities_data)


def reset_activities():
    activities_data.clear()
    activities_data.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_200():
    reset_activities()
    with TestClient(app) as client:
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data


def test_signup_for_activity_adds_participant():
    reset_activities()
    with TestClient(app) as client:
        email = "newstudent@mergington.edu"
        response = client.post("/activities/Chess Club/signup", params={"email": email})
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_duplicate_returns_400():
    reset_activities()
    with TestClient(app) as client:
        email = "duplicate@mergington.edu"
        client.post("/activities/Chess Club/signup", params={"email": email})
        response = client.post("/activities/Chess Club/signup", params={"email": email})
        assert response.status_code == 400


def test_remove_participant_success():
    reset_activities()
    with TestClient(app) as client:
        email = "removeme@mergington.edu"
        client.post("/activities/Chess Club/signup", params={"email": email})

        response = client.delete("/activities/Chess Club/participants", params={"email": email})
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]


def test_remove_participant_not_found():
    reset_activities()
    with TestClient(app) as client:
        response = client.delete("/activities/Chess Club/participants", params={"email": "ghost@mergington.edu"})
        assert response.status_code == 404


def test_activity_not_found_signup():
    reset_activities()
    with TestClient(app) as client:
        response = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
        assert response.status_code == 404


def test_activity_not_found_remove():
    reset_activities()
    with TestClient(app) as client:
        response = client.delete("/activities/Nonexistent/participants", params={"email": "a@b.com"})
        assert response.status_code == 404
