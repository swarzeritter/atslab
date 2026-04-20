import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:8000"
USERNAME = "seleniumuser"
EMAIL = "selenium@gmail.com"
PASSWORD = "selenium123"
POST_TITLE = "Selenium Test Post"
POST_CONTENT = "This post was created by Selenium WebDriver."


@pytest.fixture(scope="session")
def driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    drv = webdriver.Chrome(service=service, options=options)
    drv.set_window_size(1373, 782)
    yield drv
    drv.quit()


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL
