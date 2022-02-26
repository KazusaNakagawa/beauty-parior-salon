from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    # assert response.json() == [
    #     {'id': 1,
    #      'name': 'string',
    #      'email': 'string',
    #      'password': 'string'}
    # ]
