import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCREENSHOTS_DIR = "screenshots"


class BasePage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    def navigate(self, path):
        self.driver.get(self.base_url + path)

    def screenshot(self, step_name):
        path = os.path.join(SCREENSHOTS_DIR, f"{step_name}.png")
        self.driver.save_screenshot(path)

    def wait_for(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_url(self, partial, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.url_contains(partial)
        )

    def js(self, script, *args):
        return self.driver.execute_script(script, *args)

    def js_submit(self, email=None, password=None, username=None,
                  title=None, content=None):
        parts = []
        if username:
            parts.append(f"document.querySelector('#username').value = arguments[0];")
        if email:
            idx = 1 if username else 0
            parts.append(f"document.querySelector('#email').value = arguments[{idx}];")
        if password:
            idx = 2 if username else 1
            parts.append(f"document.querySelector('#password').value = arguments[{idx}];")
        if title:
            parts.append("document.querySelector(\"input[name='title']\").value = arguments[0];")
        if content:
            parts.append("document.querySelector(\"textarea[name='content']\").value = arguments[1];")
        parts.append("document.querySelector('form').submit();")
        args_list = [v for v in [username, email, password, title, content] if v]
        self.js(" ".join(parts), *args_list)
