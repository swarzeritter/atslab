"""
API endpoint tests — covers all routes of the Blog application.
"""


# ---------------------------------------------------------------------------
# GET / (root)
# ---------------------------------------------------------------------------

class TestRoot:
    def test_root_redirects_to_posts(self, client):
        r = client.get("/", follow_redirects=False)
        assert r.status_code in (302, 303, 307)
        assert "posts" in r.headers["location"]


# ---------------------------------------------------------------------------
# Auth — GET pages
# ---------------------------------------------------------------------------

class TestAuthPages:
    def test_register_page_returns_200(self, client):
        r = client.get("/auth/register")
        assert r.status_code == 200

    def test_login_page_returns_200(self, client):
        r = client.get("/auth/login")
        assert r.status_code == 200

    def test_login_page_redirects_when_authenticated(self, auth_client):
        r = auth_client.get("/auth/login", follow_redirects=False)
        assert r.status_code == 303
        assert "posts" in r.headers["location"]

    def test_forgot_password_page_returns_200(self, client):
        r = client.get("/auth/forgot-password")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Auth — POST register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_success_redirects_to_posts(self, client):
        r = client.post("/auth/register", data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "pass123",
        }, follow_redirects=False)
        assert r.status_code == 303
        assert r.headers["location"] == "/posts"

    def test_register_duplicate_username_returns_error(self, client):
        data = {"username": "dup", "email": "dup@example.com", "password": "pass123"}
        client.post("/auth/register", data=data)
        r = client.post("/auth/register", data={
            "username": "dup", "email": "other@example.com", "password": "pass123",
        })
        assert r.status_code == 200
        assert "вже зайняте" in r.text

    def test_register_duplicate_email_returns_error(self, client):
        client.post("/auth/register", data={
            "username": "u1", "email": "same@example.com", "password": "pass123",
        })
        r = client.post("/auth/register", data={
            "username": "u2", "email": "same@example.com", "password": "pass123",
        })
        assert r.status_code == 200
        assert "вже використовується" in r.text


# ---------------------------------------------------------------------------
# Auth — POST login / logout
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_valid_redirects_to_posts(self, client):
        client.post("/auth/register", data={
            "username": "loginuser", "email": "login@example.com", "password": "pass123",
        })
        r = client.post("/auth/login", data={
            "email": "login@example.com", "password": "pass123",
        }, follow_redirects=False)
        assert r.status_code == 303
        assert r.headers["location"] == "/posts"

    def test_login_wrong_password_returns_error(self, client):
        r = client.post("/auth/login", data={
            "email": "nobody@example.com", "password": "wrong",
        })
        assert r.status_code == 200
        assert "Невірний" in r.text

    def test_logout_redirects_to_posts(self, auth_client):
        r = auth_client.get("/auth/logout", follow_redirects=False)
        assert r.status_code == 303
        assert r.headers["location"] == "/posts"


# ---------------------------------------------------------------------------
# Auth — forgot / reset password
# ---------------------------------------------------------------------------

class TestPasswordReset:
    def test_forgot_password_unknown_email_returns_error(self, client):
        r = client.post("/auth/forgot-password", data={"email": "unknown@example.com"})
        assert r.status_code == 200
        assert "не знайдено" in r.text

    def test_forgot_password_known_email_returns_link(self, auth_client):
        r = auth_client.post("/auth/forgot-password", data={"email": "api@example.com"})
        assert r.status_code == 200
        assert "reset-password" in r.text

    def test_reset_password_invalid_token_returns_error(self, client):
        r = client.get("/auth/reset-password/invalid-token-xyz")
        assert r.status_code == 200
        assert "недійсне" in r.text.lower() or r.status_code in (200, 404)


# ---------------------------------------------------------------------------
# Posts — list and detail
# ---------------------------------------------------------------------------

class TestPostsRead:
    def test_posts_list_returns_200(self, client):
        r = client.get("/posts")
        assert r.status_code == 200

    def test_post_detail_returns_200(self, post_client):
        r = post_client.get("/posts/1")
        assert r.status_code == 200
        assert "API Test Post" in r.text

    def test_post_detail_nonexistent_returns_404(self, client):
        r = client.get("/posts/99999")
        assert r.status_code == 404

    def test_new_post_page_requires_auth(self, client):
        r = client.get("/posts/new", follow_redirects=False)
        assert r.status_code == 303
        assert "login" in r.headers["location"]

    def test_new_post_page_authenticated_returns_200(self, auth_client):
        r = auth_client.get("/posts/new")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Posts — create
# ---------------------------------------------------------------------------

class TestPostCreate:
    def test_create_post_unauthenticated_redirects_to_login(self, client):
        r = client.post("/posts", data={
            "title": "Test", "content": "Body",
        }, follow_redirects=False)
        assert r.status_code == 303
        assert "login" in r.headers["location"]

    def test_create_post_authenticated_redirects_to_detail(self, auth_client):
        r = auth_client.post("/posts", data={
            "title": "New Post", "content": "Body",
        }, follow_redirects=False)
        assert r.status_code == 303
        assert "/posts/" in r.headers["location"]


# ---------------------------------------------------------------------------
# Posts — edit
# ---------------------------------------------------------------------------

class TestPostEdit:
    def test_edit_post_page_returns_200(self, post_client):
        r = post_client.get("/posts/1/edit")
        assert r.status_code == 200

    def test_edit_post_page_requires_auth(self, client):
        r = client.get("/posts/1/edit", follow_redirects=False)
        assert r.status_code == 303
        assert "login" in r.headers["location"]

    def test_update_post_redirects_to_detail(self, post_client):
        r = post_client.post("/posts/1/edit", data={
            "title": "Updated Title", "content": "Updated Content",
        }, follow_redirects=False)
        assert r.status_code == 303
        assert "/posts/1" in r.headers["location"]

    def test_update_post_changes_content(self, post_client):
        post_client.post("/posts/1/edit", data={
            "title": "Changed", "content": "New body",
        })
        r = post_client.get("/posts/1")
        assert "Changed" in r.text


# ---------------------------------------------------------------------------
# Posts — delete
# ---------------------------------------------------------------------------

class TestPostDelete:
    def test_delete_post_redirects_to_list(self, post_client):
        r = post_client.post("/posts/1/delete", follow_redirects=False)
        assert r.status_code == 303
        assert r.headers["location"] == "/posts"

    def test_deleted_post_returns_404(self, post_client):
        post_client.post("/posts/1/delete")
        r = post_client.get("/posts/1")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

class TestComments:
    def test_add_comment_redirects_to_post(self, post_client):
        r = post_client.post("/posts/1/comments", data={
            "content": "Great post!",
        }, follow_redirects=False)
        assert r.status_code == 303
        assert "/posts/1" in r.headers["location"]

    def test_add_comment_unauthenticated_redirects_to_login(self, client):
        r = client.post("/posts/1/comments", data={
            "content": "Hi",
        }, follow_redirects=False)
        assert r.status_code == 303
        assert "login" in r.headers["location"]

    def test_delete_comment_redirects_to_post(self, post_client):
        post_client.post("/posts/1/comments", data={"content": "To delete"})
        r = post_client.post("/posts/1/comments/1/delete", follow_redirects=False)
        assert r.status_code == 303
        assert "/posts/1" in r.headers["location"]


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class TestProfile:
    def test_profile_page_returns_200(self, auth_client):
        r = auth_client.get("/profile/apiuser")
        assert r.status_code == 200
        assert "apiuser" in r.text

    def test_profile_nonexistent_returns_404(self, client):
        r = client.get("/profile/nobody")
        assert r.status_code == 404

    def test_profile_edit_page_requires_auth(self, client):
        r = client.get("/profile/edit", follow_redirects=False)
        assert r.status_code == 303
        assert "login" in r.headers["location"]

    def test_profile_edit_page_authenticated_returns_200(self, auth_client):
        r = auth_client.get("/profile/edit")
        assert r.status_code == 200

    def test_profile_edit_updates_bio(self, auth_client):
        r = auth_client.post("/profile/edit", data={
            "bio": "My new bio",
        }, follow_redirects=False)
        assert r.status_code == 303
