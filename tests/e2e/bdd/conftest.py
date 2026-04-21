import os
import sys
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pytest_bdd import given, when, then, parsers

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from webdriver.pages.auth_pages import RegisterPage, LoginPage
from webdriver.pages.posts_pages import PostsListPage, PostFormPage, PostDetailPage
from webdriver.pages.profile_page import ProfilePage

BASE_URL = "http://127.0.0.1:8000"
BDD_USERNAME = "bddtestuser"
BDD_EMAIL = "bddtest@test.com"
BDD_PASSWORD = "bdd12345"


@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    drv = webdriver.Chrome(options=options)
    drv.set_window_size(1373, 782)
    yield drv
    drv.quit()


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session", autouse=True)
def ensure_bdd_user(driver, base_url):
    """Register BDD test user once per session if not yet registered."""
    driver.get(base_url + "/auth/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
    driver.execute_script(
        "document.querySelector('#email').value = arguments[0];"
        "document.querySelector('#password').value = arguments[1];"
        "document.querySelector('form').submit();",
        BDD_EMAIL, BDD_PASSWORD,
    )
    try:
        WebDriverWait(driver, 5).until(EC.url_contains("posts"))
        driver.get(base_url + "/auth/logout")
        WebDriverWait(driver, 5).until(EC.url_contains("posts"))
    except TimeoutException:
        driver.get(base_url + "/auth/register")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.execute_script(
            "document.querySelector('#username').value = arguments[0];"
            "document.querySelector('#email').value = arguments[1];"
            "document.querySelector('#password').value = arguments[2];"
            "document.querySelector('form').submit();",
            BDD_USERNAME, BDD_EMAIL, BDD_PASSWORD,
        )
        WebDriverWait(driver, 10).until(EC.url_contains("posts"))
        driver.get(base_url + "/auth/logout")
        WebDriverWait(driver, 5).until(EC.url_contains("posts"))


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given("браузер відкрито")
def browser_open(driver, base_url):
    driver.get(base_url + "/auth/logout")
    WebDriverWait(driver, 5).until(EC.url_contains("posts"))


@given("я авторизований")
def i_am_logged_in(driver, base_url):
    driver.get(base_url + "/auth/logout")
    WebDriverWait(driver, 5).until(EC.url_contains("posts"))
    LoginPage(driver, base_url).login(BDD_EMAIL, BDD_PASSWORD)


@given("є хоча б один пост")
def there_is_at_least_one_post(driver, base_url):
    driver.get(base_url + "/posts")
    elements = driver.find_elements(By.CSS_SELECTOR, ".card-title a")
    if not elements:
        PostFormPage(driver, base_url).create_post("BDD Тестовий пост", "Вміст тестового поста")


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------

@when(parsers.parse('я реєструюсь з іменем "{username}" email "{email}" паролем "{password}"'))
def register_user(driver, base_url, username, email, password):
    RegisterPage(driver, base_url).register(username, email, password)


@when(parsers.parse('я намагаюсь увійти з email "{email}" та паролем "{password}"'))
def login_invalid_attempt(driver, base_url, email, password):
    LoginPage(driver, base_url).login_invalid(email, password)


@when(parsers.parse('я входжу з email "{email}" та паролем "{password}"'))
def login_valid(driver, base_url, email, password):
    LoginPage(driver, base_url).login(email, password)


@when("я виходжу з системи")
def logout(driver, base_url):
    LoginPage(driver, base_url).logout()


@when(parsers.parse('я створюю пост з заголовком "{title}" та вмістом "{content}"'))
def create_post(driver, base_url, title, content):
    PostFormPage(driver, base_url).create_post(title, content)


@when("я переходжу на сторінку постів")
def navigate_to_posts(driver, base_url):
    driver.get(base_url + "/posts")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))


@when("я відкриваю перший пост")
def open_first_post(driver, base_url):
    PostsListPage(driver, base_url).open_first_post()


@when(parsers.parse('я додаю коментар "{comment}"'))
def add_comment(driver, base_url, comment):
    PostDetailPage(driver, base_url).add_comment(comment)


@when("я переходжу на сторінку профайлу")
def navigate_to_profile(driver, base_url):
    ProfilePage(driver, base_url).open(BDD_USERNAME)


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------

@then("я знаходжусь на сторінці постів")
def on_posts_page(driver):
    assert "posts" in driver.current_url


@then("я знаходжусь на сторінці входу")
def on_login_page(driver):
    assert "login" in driver.current_url


@then("я знаходжусь на сторінці поста")
def on_post_detail_page(driver):
    assert "/posts/" in driver.current_url


@then("я бачу хоча б один пост")
def see_at_least_one_post(driver):
    elements = driver.find_elements(By.CSS_SELECTOR, ".card-title a")
    assert len(elements) > 0


@then("я бачу сторінку профайлу")
def see_profile_page(driver):
    assert BDD_USERNAME in driver.current_url
