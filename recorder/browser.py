import threading
from playwright.sync_api import sync_playwright

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
        done = threading.Event()

        with sync_playwright() as p:
            launcher = getattr(p, browser_key)
            browser = launcher.launch(headless=False)

            context_args = {
                "viewport": {"width": vp["width"], "height": vp["height"]},
            }
            if self._config.get("user_agent"):
                context_args["user_agent"] = self._config["user_agent"]

            browser.on("disconnected", lambda: done.set())
            context = browser.new_context(**context_args)
            context.on("close", lambda: done.set())
            page = context.new_page()
            page.on("close", lambda: done.set())
            interceptor.attach(page)
            print(f"[browser] navigating to {self._config['initial_url']}")
            page.goto(self._config["initial_url"])
            print("[browser] waiting for session to end...")
            done.wait()
            print("[browser] session ended")

        self._on_session_end(interceptor.records)
