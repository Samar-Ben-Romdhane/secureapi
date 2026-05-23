import pytest
from src.app import create_app
from src.models.models import db as _db


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret-key",
    )
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    client.post("/auth/register", json={"username": "testuser", "password": "password123"})
    resp = client.post("/auth/login", json={"username": "testuser", "password": "password123"})
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_register_success(client):
    resp = client.post("/auth/register", json={"username": "newuser", "password": "securepass"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "token" in data
    assert data["user"]["username"] == "newuser"


def test_register_duplicate(client):
    client.post("/auth/register", json={"username": "dupeuser", "password": "securepass"})
    resp = client.post("/auth/register", json={"username": "dupeuser", "password": "securepass"})
    assert resp.status_code == 409


def test_register_short_password(client):
    resp = client.post("/auth/register", json={"username": "user2", "password": "short"})
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={"username": "loginuser", "password": "password123"})
    resp = client.post("/auth/login", json={"username": "loginuser", "password": "password123"})
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "loginuser2", "password": "password123"})
    resp = client.post("/auth/login", json={"username": "loginuser2", "password": "wrongpass"})
    assert resp.status_code == 401


def test_create_task(client, auth_headers):
    resp = client.post("/tasks/", json={"title": "Buy groceries"}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()["title"] == "Buy groceries"


def test_list_tasks(client, auth_headers):
    client.post("/tasks/", json={"title": "Task 1"}, headers=auth_headers)
    client.post("/tasks/", json={"title": "Task 2"}, headers=auth_headers)
    resp = client.get("/tasks/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_update_task(client, auth_headers):
    create = client.post("/tasks/", json={"title": "Old title"}, headers=auth_headers)
    task_id = create.get_json()["id"]
    resp = client.patch(f"/tasks/{task_id}", json={"done": True}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["done"] is True


def test_delete_task(client, auth_headers):
    create = client.post("/tasks/", json={"title": "To delete"}, headers=auth_headers)
    task_id = create.get_json()["id"]
    resp = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200


def test_task_requires_auth(client):
    resp = client.get("/tasks/")
    assert resp.status_code == 401


def test_task_isolation(client):
    client.post("/auth/register", json={"username": "user_a", "password": "password123"})
    client.post("/auth/register", json={"username": "user_b", "password": "password123"})

    resp_a = client.post("/auth/login", json={"username": "user_a", "password": "password123"})
    resp_b = client.post("/auth/login", json={"username": "user_b", "password": "password123"})

    headers_a = {"Authorization": f"Bearer {resp_a.get_json()['token']}"}
    headers_b = {"Authorization": f"Bearer {resp_b.get_json()['token']}"}

    create = client.post("/tasks/", json={"title": "Private task"}, headers=headers_a)
    task_id = create.get_json()["id"]

    resp = client.get(f"/tasks/{task_id}", headers=headers_b)
    assert resp.status_code == 404
