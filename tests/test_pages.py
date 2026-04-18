def test_root_redirects(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)


def test_posts_list_loads(client):
    response = client.get("/posts")
    assert response.status_code == 200


def test_login_page_loads(client):
    response = client.get("/auth/login")
    assert response.status_code == 200


def test_register_page_loads(client):
    response = client.get("/auth/register")
    assert response.status_code == 200


def test_forgot_password_page_loads(client):
    response = client.get("/auth/forgot-password")
    assert response.status_code == 200


def test_nonexistent_post_returns_404(client):
    response = client.get("/posts/99999")
    assert response.status_code == 404


def test_nonexistent_profile_returns_404(client):
    response = client.get("/profile/nobody")
    assert response.status_code == 404
