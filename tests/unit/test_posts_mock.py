"""Unit tests for posts router with Mock/Spy — 50%+ coverage of business logic."""
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app.main import app
from app.database import Base, get_db

engine = create_engine("sqlite:///./test_mock.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.username = "mockuser"
    return user


@pytest.fixture
def auth_client(db_session, mock_user):
    """Client with mocked authenticated user."""
    def override_db():
        yield db_session

    def override_user():
        return mock_user

    app.dependency_overrides[get_db] = override_db
    from app.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = override_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def anon_client(db_session):
    """Client with no authenticated user (anonymous)."""
    def override_db():
        yield db_session

    def override_user():
        return None

    app.dependency_overrides[get_db] = override_db
    from app.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = override_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_list_posts_calls_db(db_session, mock_user):
    """Spy: verify that listing posts queries the database."""
    mock_db = MagicMock()
    mock_db.query.return_value.order_by.return_value.all.return_value = []

    def override_db():
        yield mock_db

    def override_user():
        return mock_user

    app.dependency_overrides[get_db] = override_db
    from app.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = override_user

    with TestClient(app) as c:
        response = c.get("/posts")

    assert response.status_code == 200
    mock_db.query.assert_called_once()
    app.dependency_overrides.clear()


def test_create_post_redirects(auth_client):
    response = auth_client.post("/posts", data={
        "title": "Mock post",
        "content": "Mock content",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "/posts/" in response.headers["location"]


def test_create_post_unauthenticated_redirects(anon_client):
    response = anon_client.post("/posts", data={
        "title": "title", "content": "content",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "login" in response.headers["location"]


def test_new_post_page_authenticated(auth_client):
    response = auth_client.get("/posts/new")
    assert response.status_code == 200


def test_new_post_page_unauthenticated(anon_client):
    response = anon_client.get("/posts/new", follow_redirects=False)
    assert response.status_code == 303


def test_delete_nonexistent_post(auth_client):
    response = auth_client.post("/posts/99999/delete")
    assert response.status_code == 404


def test_edit_nonexistent_post(auth_client):
    response = auth_client.get("/posts/99999/edit")
    assert response.status_code == 404


def test_add_comment_to_nonexistent_post(auth_client):
    response = auth_client.post("/posts/99999/comments", data={"content": "hi"})
    assert response.status_code == 404
