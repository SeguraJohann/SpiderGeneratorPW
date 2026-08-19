import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

BROWSERS = ["Chrome", "Firefox", "WebKit"]
DEFAULT_BROWSER = "Chrome"

VIEWPORTS = ["1920x1080", "1440x900", "1280x720", "375x812"]
DEFAULT_VIEWPORT = "1920x1080"

DEFAULT_CAPTURE_SCOPE = "all"
CAPTURE_SCOPE_OPTIONS = ["all", "fetch_xhr", "document", "script"]

NOISE_PATTERNS = [
    "google-analytics.com",
    "googletagmanager.com",
    "analytics.google.com",
    "connect.facebook.net",
    "facebook.com/tr",
    "hotjar.com",
    "sentry.io",
    "ingest.sentry.io",
    "cloudflareinsights.com",
    "static.cloudflareinsights.com",
    "doubleclick.net",
    "googlesyndication.com",
    "adservice.google.com",
]

STATIC_EXTENSIONS = [
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot",
    ".css",
]
