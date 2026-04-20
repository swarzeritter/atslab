from selenium.webdriver.common.by import By
from .base_page import BasePage


class PostsListPage(BasePage):
    def open(self):
        self.navigate("/posts")
        self.wait_for((By.CSS_SELECTOR, "h1"))

    def open_first_post(self):
        self.navigate("/posts")
        self.wait_for((By.CSS_SELECTOR, ".card-title a"))
        self.js("document.querySelector('.card-title a').click()")
        self.wait_for((By.CSS_SELECTOR, "article"))


class PostFormPage(BasePage):
    def create_post(self, title, content):
        self.navigate("/posts/new")
        self.wait_for((By.CSS_SELECTOR, "input[name='title']"))
        self.js(
            "document.querySelector(\"input[name='title']\").value = arguments[0];"
            "document.querySelector(\"textarea[name='content']\").value = arguments[1];"
            "document.querySelector('form').submit();",
            title, content
        )
        self.wait_for_url("/posts/")
        self.screenshot("04_create_post")

    def edit_post(self, content):
        self.wait_for((By.CSS_SELECTOR, "textarea[name='content']"))
        self.js(
            "document.querySelector(\"textarea[name='content']\").value = arguments[0];"
            "document.querySelector('form').submit();",
            content
        )
        self.wait_for((By.CSS_SELECTOR, "article"))
        self.screenshot("07_edit_post")


class PostDetailPage(BasePage):
    def view(self):
        self.wait_for((By.CSS_SELECTOR, "article"))
        self.screenshot("05_view_post")

    def add_comment(self, content):
        self.wait_for((By.CSS_SELECTOR, "textarea[name='content']"))
        self.js(
            "document.querySelector(\"textarea[name='content']\").value = arguments[0];"
            "document.querySelector('#comments form').submit();",
            content
        )
        self.wait_for((By.CSS_SELECTOR, "article"))
        self.screenshot("06_add_comment")

    def open_edit(self):
        self.wait_for((By.CSS_SELECTOR, "a[href*='/posts/'][href*='/edit']"))
        self.js("document.querySelector(\"a[href*='/posts/'][href*='/edit']\").click()")
        self.screenshot("07_edit_post_open")

    def delete_post(self):
        self.wait_for((By.CSS_SELECTOR, ".btn-outline-danger"))
        self.js(
            "document.querySelector('.btn-outline-danger').closest('form').onsubmit = null;"
            "document.querySelector('.btn-outline-danger').click();"
        )
        self.wait_for_url("posts")
        self.screenshot("09_delete_post")
