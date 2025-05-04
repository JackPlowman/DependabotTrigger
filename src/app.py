from playwright.sync_api import sync_playwright

from structlog import get_logger, stdlib

logger: stdlib.BoundLogger = get_logger()


def app() -> None:
    """Main application function."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.github.com/login")

        page.wait_for_url("https://github.com/", timeout=30000)
