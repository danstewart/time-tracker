from playwright.sync_api import Page, expect
from tests.helpers import login


def test_clock_in_out(page: Page):
    """
    Test we can click in, start a break, end a break and clock out
    """
    login(page)

    # Clock in
    page.get_by_text("Clock In").click()
    expect(page.get_by_text("Clock Out")).to_be_visible()

    # Go on break
    page.get_by_text("Start Break").click()
    expect(page.get_by_text("End Break")).to_be_visible()

    # End break
    page.get_by_text("End Break").click()
    expect(page.get_by_text("Start Break")).to_be_visible()

    # Clock out
    page.get_by_text("Clock Out").click()
    expect(page.get_by_text("Clock In")).to_be_visible()


def test_add_time_log(page: Page):
    """
    Test we can manually add a time log entry
    """
    from datetime import datetime, timedelta

    today = datetime.today()

    one_am = (today + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
    two_am = (today + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")

    login(page)

    # Expand form
    page.get_by_text("Log Time").click()
    page.locator("#start-time").first.evaluate(f"el => el.value = '{one_am}'")
    page.locator("#end-time").first.evaluate(f"el => el.value = '{two_am}'")
    page.locator("[name=note]").first.fill("test")
    page.get_by_text("Save changes").first.click()

    # NOTE: The first test will add the row with id=1
    expect(page.locator("#accordion-2-header")).to_be_attached()
