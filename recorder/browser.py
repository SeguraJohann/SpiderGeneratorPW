from playwright.sync_api import sync_playwright
import time

BROWSER_MAP = {
    "Chrome": "chromium",
    "Firefox": "firefox",
    "WebKit": "webkit",
}


class BrowserSession:
    def __init__(self, config, on_session_end):
        self._config = config
        self._on_session_end = on_session_end

    def start(self):
        from recorder.interceptor import Interceptor

        interceptor = Interceptor(self._config)
        vp = self._config["viewport"]
        browser_key = BROWSER_MAP.get(self._config["browser"], "chromium")

        with sync_playwright() as p:
            launcher = getattr(p, browser_key)
            browser = launcher.launch(headless=False)

            context_args = {
                "viewport": {"width": vp["width"], "height": vp["height"]},
            }
            if self._config.get("user_agent"):
                context_args["user_agent"] = self._config["user_agent"]

            context = browser.new_context(**context_args)
            page = context.new_page()
            interceptor.attach(page)
            page.goto(self._config["initial_url"])

            while browser.is_connected():
                time.sleep(0.5)

        self._on_session_end(interceptor.records)
