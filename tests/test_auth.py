class TestRegister:

    def test_register_success(self, client):
        response = client.post("/auth/register", json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "password123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@test.com"
        assert "id" in data
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client, user_headers):
        response = client.post("/auth/register", json={
            "username": "testuser",
            "email": "different@test.com",
            "password": "password123"
        })
        assert response.status_code == 400
        assert "Username already taken" in response.json()["error"]["message"]

    def test_register_duplicate_email(self, client, user_headers):
        response = client.post("/auth/register", json={
            "username": "differentuser",
            "email": "test@test.com",
            "password": "password123"
        })
        assert response.status_code == 400
        assert "Email already registered" in response.json()["error"]["message"]

    def test_register_invalid_data(self, client):
        response = client.post("/auth/register", json={
            "username": "x"
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        response = client.post("/auth/register", json={
            "username": "validuser",
            "email": "valid@test.com",
            "password": "123"
        })
        assert response.status_code == 422


class TestLogin:

    def test_login_success(self, client, user_headers):
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "test1234"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"

    def test_login_wrong_password(self, client, user_headers):
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["error"]["message"]

    def test_login_wrong_username(self, client):
        response = client.post("/auth/login", json={
            "username": "nobody",
            "password": "password123"
        })
        assert response.status_code == 401

    def test_login_returns_valid_token(self, client, user_headers):
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "test1234"
        })
        token = response.json()["access_token"]
        cart_response = client.get(
            "/cart/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert cart_response.status_code == 200