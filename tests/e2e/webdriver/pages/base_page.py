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
