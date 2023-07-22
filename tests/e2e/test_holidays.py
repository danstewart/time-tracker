from playwright.sync_api import Page, expect

from tests.helpers import login, open_menu_and_click


def test_upcoming_holidays(page: Page):
    """
    Test we can view the upcoming holiday list
    """
    login(page)

    open_menu_and_click("Holidays", page)

    # Should be redirected to settings
    expect(page).to_have_url("http://localhost:5000/settings/general")
    expect(page.locator(".toast-body")).to_contain_text("Please set a holiday location to view the holidays list")

    # Save holiday location
    page.locator("#holiday_location").select_option("Scotland")
    page.get_by_text("Save").click()
    expect(page).to_have_url("http://localhost:5000/dash")
    expect(page.locator(".toast-body")).to_contain_text("Settings saved")

    open_menu_and_click("Holidays", page)
    expect(page).to_have_url("http://localhost:5000/holidays")
    expect(page.get_by_text("Upcoming Holidays")).to_be_visible()


def test_previous_holidays(page: Page):
    """
    Test we can view the upcoming holiday list
    """
    login(page)

    open_menu_and_click("Holidays", page)
    page.get_by_text("History").click()
    expect(page).to_have_url("http://localhost:5000/holidays/history")
    expect(page.get_by_text("Previous Holidays")).to_be_visible()
