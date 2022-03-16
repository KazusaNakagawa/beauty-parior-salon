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
