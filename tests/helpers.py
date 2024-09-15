from playwright.sync_api import Page, expect


def login(page: Page):
    """
    Log in to the site
    """
    page.goto("http://localhost:5000/login")

    page.locator("#userEmail").fill("test@example.com")
    page.locator("#userPassword").fill("test")
    page.locator("button[value=login]").click()

    expect(page.get_by_text("Clock In")).to_be_attached()


def open_menu_and_click(text: str, page: Page):
    """
    Open the navigation menu and click the item with the given text
    """
    menu = page.locator("#menu")
    menu.locator("li > a").first.click()
    menu.get_by_text(text).click()


def execute_sql(statements: list[str]):
    """
    Helper for cleaning up after tests
    Executes a list of SQL statements
    """
    import sqlalchemy as sa

    engine = sa.create_engine("sqlite:////home/app/log-my-time/db/time.test.db")

    with engine.connect() as conn:
        for statement in statements:
            conn.execute(sa.text(statement))
        conn.execute(sa.text("COMMIT"))
