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

            print(f"[browser] navigating to {self._config['initial_url']}")
            page.goto(self._config["initial_url"])

            print("[browser] waiting for session to end — close the browser window to finish.")
            try:
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass

            print(f"[browser] session ended — {len(interceptor.records)} requests captured.")
            try:
                browser.close()
            except Exception:
                pass

        self._on_session_end(interceptor.records)
