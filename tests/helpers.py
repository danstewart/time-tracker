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
    Execute a list of SQL statements
    Useful for test set up and teardown
    """
    from sqlalchemy import text

    from app import create_app, db

    app = create_app(test_mode=True)

    # TODO: Fix this
    with app.app_context(), app.test_request_context():
        with db.sessionmaker() as session:
            for statement in statements:
                session.execute(text(statement))
            session.commit()
