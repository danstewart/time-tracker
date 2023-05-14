from playwright.sync_api import Page, expect


def login(page: Page):
    # Log in
    page.goto("http://localhost:5000/login")

    page.locator("#userEmail").fill("test@example.com")
    page.locator("#userPassword").fill("test")
    page.locator("button[value=login]").click()

    expect(page.get_by_text("Clock In")).to_be_attached()
