from playwright.sync_api import Page, expect

from tests.helpers import execute_sql, login, open_menu_and_click


def test_general_settings(page: Page):
    """
    Test can view and edit general settings
    """
    login(page)

    open_menu_and_click("Settings", page)
    expect(page).to_have_url("http://localhost:5000/settings")

    # Save holiday location
    page.locator("#holiday_location").select_option("Scotland")
    page.get_by_text("Save").click()
    expect(page).to_have_url("http://localhost:5000/dash")
    expect(page.locator(".toast-body")).to_contain_text("Settings saved")

    # Teardown changes
    execute_sql(["UPDATE settings SET holiday_location = NULL"])
