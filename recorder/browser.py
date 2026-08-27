import threading
from playwright.sync_api import sync_playwright

BROWSER_MAP = {
    "Chrome": "chromium",
    "Firefox": "firefox",
    "WebKit": "webkit",
}


class BrowserSession:
    def __init__(self, config, record_queue, on_session_end):
        self._config = config
        self._queue = record_queue
        self._on_session_end = on_session_end
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def start_in_thread(self):
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        from recorder.interceptor import Interceptor

        interceptor = Interceptor(self._config, record_queue=self._queue)
        vp = self._config["viewport"]
        browser_key = BROWSER_MAP.get(self._config["browser"], "chromium")

        with sync_playwright() as p:
            launcher = getattr(p, browser_key)
            browser = launcher.launch(headless=False, args=["--start-maximized"])

            context_args = {
                "viewport": None,
            }
            if self._config.get("user_agent"):
                context_args["user_agent"] = self._config["user_agent"]

            context = browser.new_context(**context_args)
            page = context.new_page()
            interceptor.attach(page)
            page.goto(self._config["initial_url"])

            while not self._stop_event.is_set():
                page.wait_for_timeout(200)

            browser.close()

        self._on_session_end(interceptor.records)
