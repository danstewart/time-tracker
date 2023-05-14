from playwright.sync_api import Page, expect


def test_login_for_success(page: Page):
    page.goto("http://localhost:5000/login")

    page.locator("#userEmail").fill("test@example.com")
    page.locator("#userPassword").fill("test")
    page.locator("button[value=login]").click()

    expect(page.get_by_text("Clock In")).to_be_attached()


def test_login_for_failure(page: Page):
    page.goto("http://localhost:5000/login")

    page.locator("#userEmail").fill("test@example.com")
    page.locator("#userPassword").fill("wrong")
    page.locator("button[value=login]").click()

    expect(page.get_by_text("Invalid username or password.")).to_be_visible()
