def test_create_post_unauthenticated(client):
    response = client.post("/posts", data={
        "title": "Test",
        "content": "Content",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "login" in response.headers["location"]


def test_create_post_authenticated(registered_client):
    response = registered_client.post("/posts", data={
        "title": "My first post",
        "content": "Hello world",
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "/posts/" in response.headers["location"]


def test_post_detail_visible(registered_client):
    registered_client.post("/posts", data={
        "title": "Visible post",
        "content": "Some content here",
    })
    response = registered_client.get("/posts/1")
    assert response.status_code == 200
    assert "Visible post" in response.text


def test_add_comment(registered_client):
    registered_client.post("/posts", data={
        "title": "Post with comment",
        "content": "Content",
    })
    response = registered_client.post("/posts/1/comments", data={
        "content": "Nice post!",
    }, follow_redirects=False)
    assert response.status_code == 303


def test_delete_post(registered_client):
    registered_client.post("/posts", data={
        "title": "To be deleted",
        "content": "Delete me",
    })
    response = registered_client.post("/posts/1/delete", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/posts"
