import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """
    Create fresh tables before EACH test.
    Drop after each test.
    This ensures complete isolation between tests.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(setup_database):
    return TestClient(app)


@pytest.fixture(scope="function")
def db(setup_database):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def admin_headers(client, db):
    """Create admin user and return auth headers."""
    # Register
    client.post("/auth/register", json={
        "username": "adminuser",
        "email": "admin@test.com",
        "password": "admin1234"
    })

    # Make admin in DB
    from app.models.user import User
    user = db.query(User).filter(User.username == "adminuser").first()
    user.is_admin = True
    db.commit()

    # Login
    response = client.post("/auth/login", json={
        "username": "adminuser",
        "password": "admin1234"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def user_headers(client):
    """Create regular user and return auth headers."""
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@test.com",
        "password": "test1234"
    })
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "test1234"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def sample_category(client, admin_headers):
    """Create and return a test category."""
    response = client.post("/categories/", json={
        "name": "Electronics",
        "description": "Electronic items"
    }, headers=admin_headers)
    assert response.status_code == 201, f"Category creation failed: {response.json()}"
    return response.json()


@pytest.fixture(scope="function")
def sample_product(client, admin_headers, sample_category):
    """Create and return a test product."""
    response = client.post("/products/", json={
        "name": "Test iPhone",
        "price": 79999.0,
        "stock": 10,
        "category_id": sample_category["id"],
        "description": "Test phone"
    }, headers=admin_headers)
    assert response.status_code == 201, f"Product creation failed: {response.json()}"
    return response.json()