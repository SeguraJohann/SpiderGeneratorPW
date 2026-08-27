from datetime import datetime
from urllib.parse import urlparse

from config.defaults import NOISE_PATTERNS, STATIC_EXTENSIONS

SCOPE_MAP = {
    "fetch_xhr": {"xhr", "fetch"},
    "document": {"document"},
    "script": {"script"},
}

TEXT_TYPES = {
    "application/json",
    "text/html",
    "text/plain",
    "text/xml",
    "application/xml",
    "application/x-www-form-urlencoded",
}


class Interceptor:
    def __init__(self, config, record_queue=None):
        self._config = config
        self._scope = config["capture_scope"]
        self._filter_noise = config["filter_noise"]
        self._domain_scope = config["domain_scope"]
        self._response_body_mode = config.get("response_body_mode", "text")
        self._origin_host = urlparse(config["initial_url"]).hostname or ""
        self._queue = record_queue
        self.records = []
        self._index = 0
        self._pending = {}

    def attach(self, page):
        page.on("response", self._on_response)
        page.on("requestfinished", self._on_request_finished)
        page.on("requestfailed", self._on_request_failed)

    def _allowed_resource_types(self):
        if "all" in self._scope:
            return None
        types = set()
        for key in self._scope:
            types |= SCOPE_MAP.get(key, set())
        return types

    def _should_capture(self, request):
        allowed = self._allowed_resource_types()
        if allowed is not None and request.resource_type not in allowed:
            return False

        url = request.url
        parsed = urlparse(url)
        host = parsed.hostname or ""

        if self._domain_scope == "main":
            if host != self._origin_host:
                return False
        elif self._domain_scope == "subdomains":
            if not (host == self._origin_host or host.endswith(f".{self._origin_host}")):
                return False

        if self._filter_noise:
            for pattern in NOISE_PATTERNS:
                if pattern in url:
                    return False
            from urllib.parse import unquote
            clean_path = unquote(parsed.path).split("?")[0].lower()
            if any(clean_path.endswith(ext) for ext in STATIC_EXTENSIONS):
                return False

        return True

    def _on_response(self, response):
        request = response.request
        if not self._should_capture(request):
            return

        self._index += 1

        print(f"[interceptor] captured [{self._index:03}] {request.method} {request.url} → {response.status}")

        record = {
            "index": self._index,
            "method": request.method,
            "url": request.url,
            "request_headers": dict(request.headers),
            "payload": request.post_data,
            "status": response.status,
            "response_headers": dict(response.headers),
            "response_body": None,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": None,
            "type": request.resource_type,
            "origin_page": request.frame.url if request.frame else None,
            "notes": [],
            "excluded": False,
            "parameters": [],
            "repeated": 1,
            "response_file": None,
        }
        self.records.append(record)
        self._pending[id(request)] = record
        if self._queue is not None:
            self._queue.put(record)

    def _on_request_finished(self, request):
        record = self._pending.pop(id(request), None)
        if record is None:
            return

        try:
            response = request.response()
            if response is None:
                return
            if 300 <= record["status"] < 400:
                return
            content_type = response.headers.get("content-type", "")
            base_type = content_type.split(";")[0].strip()
            if self._response_body_mode == "all_text":
                readable = base_type.startswith("text/") or base_type.startswith("application/")
            else:
                readable = base_type in TEXT_TYPES
            if readable:
                record["response_body"] = response.text()
        except Exception as e:
            print(f"[interceptor] body read error for {request.url}: {e}")

    def _on_request_failed(self, request):
        self._pending.pop(id(request), None)
        if not self._should_capture(request):
            return
        print(f"[interceptor] failed: {request.method} {request.url} — {request.failure}")
