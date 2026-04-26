import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# use sqlite for tests so we don't need a running postgres
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def get_auth_header():
    """register a test user and return the auth header"""
    client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
    })
    resp = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "testpass123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_signup_and_login():
    resp = client.post("/auth/signup", json={
        "email": "new@example.com",
        "password": "pass123",
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "new@example.com"

    resp = client.post("/auth/login", data={
        "username": "new@example.com",
        "password": "pass123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_create_and_list_jobs():
    headers = get_auth_header()

    resp = client.post("/jobs/", json={
        "company": "Anthropic",
        "role": "ML Engineer",
        "status": "applied",
        "location": "San Francisco",
    }, headers=headers)
    assert resp.status_code == 201
    job_id = resp.json()["id"]

    resp = client.get("/jobs/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # test the stats endpoint
    resp = client.get("/jobs/stats", headers=headers)
    assert resp.json()["total"] == 1
    assert resp.json()["by_status"]["applied"] == 1


def test_update_job_status():
    headers = get_auth_header()

    resp = client.post("/jobs/", json={
        "company": "Google",
        "role": "SWE",
    }, headers=headers)
    job_id = resp.json()["id"]

    resp = client.patch(f"/jobs/{job_id}", json={
        "status": "interview",
        "notes": "onsite scheduled for next week",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "interview"


def test_delete_job():
    headers = get_auth_header()

    resp = client.post("/jobs/", json={
        "company": "Meta",
        "role": "Data Scientist",
    }, headers=headers)
    job_id = resp.json()["id"]

    resp = client.delete(f"/jobs/{job_id}", headers=headers)
    assert resp.status_code == 204

    resp = client.get(f"/jobs/{job_id}", headers=headers)
    assert resp.status_code == 404


def test_filter_by_status():
    headers = get_auth_header()

    client.post("/jobs/", json={"company": "A", "role": "SWE", "status": "applied"}, headers=headers)
    client.post("/jobs/", json={"company": "B", "role": "SWE", "status": "interview"}, headers=headers)
    client.post("/jobs/", json={"company": "C", "role": "SWE", "status": "applied"}, headers=headers)

    resp = client.get("/jobs/?status=applied", headers=headers)
    assert len(resp.json()) == 2

    resp = client.get("/jobs/?status=interview", headers=headers)
    assert len(resp.json()) == 1
