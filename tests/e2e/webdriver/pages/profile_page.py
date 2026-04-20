from selenium.webdriver.common.by import By
from .base_page import BasePage


class ProfilePage(BasePage):
    def open(self, username):
        self.navigate(f"/profile/{username}")
        self.wait_for((By.CSS_SELECTOR, "h1, h2"))
        self.screenshot("08_view_profile")
