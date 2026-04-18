def test_register_success(client):
    response = client.post("/auth/register", data={
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/posts"


def test_register_duplicate_username(client):
    data = {"username": "dupuser", "email": "dup@example.com", "password": "pass123"}
    client.post("/auth/register", data=data)
    response = client.post("/auth/register", data={
        "username": "dupuser",
        "email": "other@example.com",
        "password": "pass123",
    })
    assert response.status_code == 200
    assert "вже зайняте" in response.text


def test_register_duplicate_email(client):
    data = {"username": "user1", "email": "same@example.com", "password": "pass123"}
    client.post("/auth/register", data=data)
    response = client.post("/auth/register", data={
        "username": "user2",
        "email": "same@example.com",
        "password": "pass123",
    })
    assert response.status_code == 200
    assert "вже використовується" in response.text


def test_login_invalid_credentials(client):
    response = client.post("/auth/login", data={
        "email": "nobody@example.com",
        "password": "wrongpass",
    })
    assert response.status_code == 200
    assert "Невірний" in response.text


def test_login_valid_credentials(client):
    client.post("/auth/register", data={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123",
    })
    response = client.post("/auth/login", data={
        "email": "login@example.com",
        "password": "password123",
    }, follow_redirects=False)
    assert response.status_code == 303


def test_logout(registered_client):
    response = registered_client.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 303


def test_forgot_password_unknown_email(client):
    response = client.post("/auth/forgot-password", data={"email": "unknown@example.com"})
    assert response.status_code == 200
    assert "не знайдено" in response.text


def test_forgot_password_known_email(registered_client):
    response = registered_client.post("/auth/forgot-password", data={"email": "test@example.com"})
    assert response.status_code == 200
    assert "reset-password" in response.text
