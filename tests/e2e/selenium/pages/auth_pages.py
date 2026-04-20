from selenium.webdriver.common.by import By
from .base_page import BasePage


class RegisterPage(BasePage):
    def register(self, username, email, password):
        self.navigate("/auth/register")
        self.wait_for((By.ID, "username"))
        self.js(
            "document.querySelector('#username').value = arguments[0];"
            "document.querySelector('#email').value = arguments[1];"
            "document.querySelector('#password').value = arguments[2];"
            "document.querySelector('form').submit();",
            username, email, password
        )
        self.wait_for_url("posts")
        self.screenshot("01_register")


class LoginPage(BasePage):
    def login(self, email, password):
        self.navigate("/auth/login")
        self.wait_for((By.ID, "email"))
        self.js(
            "document.querySelector('#email').value = arguments[0];"
            "document.querySelector('#password').value = arguments[1];"
            "document.querySelector('form').submit();",
            email, password
        )
        self.wait_for_url("posts")
        self.screenshot("03_login_valid")

    def login_invalid(self, email, password):
        self.navigate("/auth/login")
        self.wait_for((By.ID, "email"))
        self.js(
            "document.querySelector('#email').value = arguments[0];"
            "document.querySelector('#password').value = arguments[1];"
            "document.querySelector('form').submit();",
            email, password
        )
        self.screenshot("02_login_invalid")
        return self.driver.current_url

    def logout(self):
        self.navigate("/auth/logout")
        self.wait_for_url("posts")
        self.screenshot("10_logout")
