import pytest
from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_read_main():
    response = client.get("/users/")
    assert response.status_code == 200


def test_create_upload_file():
    with open("media/sample.m4a", "rb") as f:
        response = client.post("/uploadfile/", files={"upload_file": ("sample.m4a", f, "audio/x-m4a")})
    assert response.status_code == 200
    assert response.json() == {"filename": "sample.m4a"}


def test_create_file():
    files = {
        "file": open("media/sample.m4a", "rb"),
        "fileb": ("sample.m4a", open("media/sample.m4a", "rb"), "audio/x-m4a"),
    }
    payload = {"manager_user_id": "m00001"}

    response = client.post("/files-from/", files=files, data=payload)

    assert response.status_code == 200
    assert response.json() == {
        'file_size': 0,
        'fileb_content_type': 'audio/x-m4a',
        'manager_user_id': 'm00001'}


def test_create_user():
    response = client.post(
        "/users/",
        json={"name": "test_user", "email": "deadpool@example.com", "password": "chimichangas4life"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert "id" in data
    user_id = data["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert data["id"] == user_id


def test_delete_user(user_id=1):
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    res_user_id = data["id"]
    assert res_user_id == user_id


def test_my_fruit(my_fruit):
    assert my_fruit == 'apple'


def test_client_user(client_user, user_id=1):
    res = client_user(user_id=user_id)
    res2 = res.__next__()
    assert res2.status_code == 200
    assert res2.json() == {
        'name': 'test_user',
        'email': 'deadpool@example.com',
        'id': user_id,
        'is_active': True,
        'items': []
    }
    res.__next__()
