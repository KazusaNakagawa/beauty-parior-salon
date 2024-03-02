import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.app import app, get_db

client = TestClient(app)

# ref: https://fastapi.tiangolo.com/advanced/testing-database/
# Test is sqlite
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# Gihub Actions is postgres
SQLALCHEMY_DATABASE_URL = "dialect+driver://username:password@host:port/database"


engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Setup clean DB init
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def my_fruit():
    return "apple"


@pytest.fixture
def client_user():
    """ユーザーを作成し後処理で削除"""

    def _client_user(user_id=1, name="test_user", email="deadpool@example.com", password="chimichangas4life"):
        res = client.post(
            "/users/",
            json={
                "name": name,
                "email": email,
                "password": password,
            },
        )
        yield res
        # delete test user
        res = client.delete(f"/users/{user_id}")
        yield res

    return _client_user
