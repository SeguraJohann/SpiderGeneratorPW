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
    def __init__(self, config):
        self._config = config
        self._scope = config["capture_scope"]
        self._filter_noise = config["filter_noise"]
        self._domain_scope = config["domain_scope"]
        self._origin_host = urlparse(config["initial_url"]).hostname or ""
        self.records = []
        self._pending = {}
        self._index = 0

    def attach(self, page):
        page.on("request", self._on_request)
        page.on("requestfinished", self._on_request_finished)

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
            path = parsed.path.lower()
            if any(path.endswith(ext) for ext in STATIC_EXTENSIONS):
                return False

        return True

    def _on_request(self, request):
        if not self._should_capture(request):
            return
        print(f"[interceptor] request: {request.method} {request.url}")
        self._pending[id(request)] = datetime.now()

    def _on_request_finished(self, request):
        key = id(request)
        if key not in self._pending:
            return

        started_at = self._pending.pop(key)
        duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)

        try:
            response = request.response()
        except Exception as e:
            print(f"[interceptor] error getting response: {e}")
            return

        if response is None:
            print(f"[interceptor] response is None for {request.url}")
            return

        body = self._read_body(response)

        self._index += 1
        record = {
            "index": self._index,
            "method": request.method,
            "url": request.url,
            "request_headers": dict(request.headers),
            "payload": request.post_data,
            "status": response.status,
            "response_headers": dict(response.headers),
            "response_body": body,
            "timestamp": started_at.isoformat(),
            "duration_ms": duration_ms,
            "type": request.resource_type,
            "origin_page": request.frame.url if request.frame else None,
            "notes": [],
            "excluded": False,
            "parameters": [],
            "repeated": 1,
            "response_file": None,
        }
        self.records.append(record)

    def _read_body(self, response):
        try:
            content_type = response.headers.get("content-type", "")
            base_type = content_type.split(";")[0].strip()
            if base_type in TEXT_TYPES:
                return response.text()
        except Exception:
            pass
        return None
