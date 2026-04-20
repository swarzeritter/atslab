"""
Selenium WebDriver e2e tests for the Blog application.
Uses Page Object Model pattern for maintainability.
"""
import pytest
from .conftest import USERNAME, EMAIL, PASSWORD, POST_TITLE, POST_CONTENT
from .pages.auth_pages import RegisterPage, LoginPage
from .pages.posts_pages import PostsListPage, PostFormPage, PostDetailPage
from .pages.profile_page import ProfilePage


@pytest.mark.usefixtures("driver")
class TestBlog:

    def test_01_register(self, driver, base_url):
        page = RegisterPage(driver, base_url)
        page.register(USERNAME, EMAIL, PASSWORD)
        assert "posts" in driver.current_url

    def test_02_logout_after_register(self, driver, base_url):
        page = LoginPage(driver, base_url)
        page.logout()
        assert "posts" in driver.current_url

    def test_03_login_invalid(self, driver, base_url):
        page = LoginPage(driver, base_url)
        url = page.login_invalid(EMAIL, "wrongpassword")
        assert "login" in url

    def test_04_login_valid(self, driver, base_url):
        page = LoginPage(driver, base_url)
        page.login(EMAIL, PASSWORD)
        assert "posts" in driver.current_url

    def test_05_create_post(self, driver, base_url):
        page = PostFormPage(driver, base_url)
        page.create_post(POST_TITLE, POST_CONTENT)
        assert "/posts/" in driver.current_url

    def test_06_view_post(self, driver, base_url):
        list_page = PostsListPage(driver, base_url)
        list_page.open_first_post()
        detail = PostDetailPage(driver, base_url)
        detail.view()
        assert "posts" in driver.current_url

    def test_07_add_comment(self, driver, base_url):
        list_page = PostsListPage(driver, base_url)
        list_page.open_first_post()
        detail = PostDetailPage(driver, base_url)
        detail.add_comment("Great post!")
        assert "posts" in driver.current_url

    def test_08_edit_post(self, driver, base_url):
        list_page = PostsListPage(driver, base_url)
        list_page.open_first_post()
        detail = PostDetailPage(driver, base_url)
        detail.open_edit()
        form = PostFormPage(driver, base_url)
        form.edit_post("Updated content for the post.")
        assert "posts" in driver.current_url

    def test_09_view_profile(self, driver, base_url):
        page = ProfilePage(driver, base_url)
        page.open(USERNAME)
        assert USERNAME in driver.current_url

    def test_10_delete_post(self, driver, base_url):
        list_page = PostsListPage(driver, base_url)
        list_page.open_first_post()
        detail = PostDetailPage(driver, base_url)
        detail.delete_post()
        assert "posts" in driver.current_url

    def test_11_logout(self, driver, base_url):
        page = LoginPage(driver, base_url)
        page.logout()
        assert "posts" in driver.current_url
