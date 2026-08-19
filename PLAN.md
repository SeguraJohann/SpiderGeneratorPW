# Project Plan — SpiderGeneratorPW

## Status
> Planning complete. No development starts until this document is approved.

---

## Overview

A desktop tool that opens a browser session, intercepts and records all network
requests made during manual navigation, allows the user to annotate the session,
and on finish generates a structured set of output files: logs, curls, responses,
and optionally basic spider scripts.

The goal is to reduce the work of a spider developer when building a new scraper
from scratch or when diagnosing why an existing one broke.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Tkinter |
| Browser automation | Playwright (headed) |
| Script templating | Jinja2 |
| Language | Python 3.10+ |
| Storage | Flat files only (JSON, TXT, SH) |

---

## Application Flow

```
1. Config form (Tkinter)
        ↓
2. Browser launches (Playwright headed)
   + Annotation panel opens (Tkinter, parallel window)
        ↓
3. User navigates — requests are intercepted and recorded in real time
   User annotates via panel (notes, exclude, mark as parameter)
        ↓
4. User clicks Finish
        ↓
5. Processing: filter, deduplicate, order, resolve parameters
        ↓
6. Output files generated in structured directory
```

---

## Stage 1 — Config Form (Tkinter)

Single window with a basic section and a collapsible advanced section.
On submit, the form validates required fields and launches the browser.

### Basic section

| Field | Type | Default | Required |
|-------|------|---------|----------|
| Source name | Text input | — | Yes |
| Initial URL | Text input | — | Yes |
| Browser | Dropdown | Chrome | Yes |
| Output directory | Folder picker | `./output/` | Yes |

### Output — checkboxes

| Option | Default | Notes |
|--------|---------|-------|
| Logs (curls + responses + navigation) | ✅ | Core output |
| Spider — `requests` | ☐ | Experimental |
| Spider — Playwright | ☐ | Experimental |
| Spider — Scrapy | ☐ disabled | v2 — reserved for defined Scrapy project structure |

### Advanced section (collapsed by default)

**Capture scope — checkboxes:**
- `All` — when selected, deselects all others. Default: ✅
- `Fetch / XHR`
- `Document`
- `Script (JS)`

| Field | Type | Default |
|-------|------|---------|
| Domain scope | Radio | Main domain only / Include subdomains |
| Filter noise (analytics, tracking, CDN) | Toggle | ON |
| Viewport | Dropdown | 1920×1080 |
| User agent | Text input | Default browser UA |

---

## Stage 2 — Browser + Annotation Panel

Two windows open simultaneously:
- Playwright headed browser at the initial URL
- Tkinter annotation panel (small, always on top)

### Annotation panel layout

- Scrollable real-time list of captured requests (method + URL + status code)
- Selected request actions:
  - `Add note` — free text, attached to that request
  - `Exclude` — marks request as noise, excluded from all outputs
  - `Mark as parameter` — opens sub-dialog (see parameters section)
- Free-text session note field + `Add` button — appends a timestamped narrative note (not tied to a specific request), used for context like "filling login form" or "starting pagination"
- `Finish` button — stops recording and triggers output generation

> **Note:** Real-time list adds threading complexity (browser and Tkinter run in
> separate threads, events passed via queue). If it causes instability during
> development, it will be simplified to a counter + finish button only, with the
> full list visible only in the output files.

---

## Stage 3 — Recording

### Captured per request

- Method, URL, headers, payload / body
- Status code, response headers, response body
- Timestamp, duration (ms)
- Request type (Fetch, XHR, Document, Script, Other)
- Origin page URL
- User annotations (notes, excluded flag, parameter markers)

### Automatic filtering (when noise filter is ON)

Auto-exclude requests matching known patterns:
- Google Analytics / Tag Manager
- Meta Pixel
- Hotjar
- Sentry
- Cloudflare Beacon
- Static assets: fonts, images, CSS (when scope is not `All`)

### Deduplication

Repeated identical requests (same method + URL + payload) are collapsed into one
entry with a `repeated: N` count. Useful for polling patterns.

---

## Stage 4 — Parameters

When the user marks a field as a parameter via the annotation panel:

Sub-dialog fields:
- Parameter name (e.g. `name`, `query`, `page`)
- Location: query string / payload body / URL path segment
- Type:
  - Single value — user provides at runtime via CLI arg
  - List — user provides comma-separated values
  - Alphabetic range — iterates a–z automatically
  - Numeric range — start / end / step

The generated spider uses `argparse` CLI args for all parameters.

---

## Stage 5 — Processing (on Finish)

1. Remove excluded requests
2. Deduplicate
3. Sort chronologically
4. Resolve parameter placeholders in URLs and payloads
5. Build `navigation.txt` interleaving requests and session notes
6. Index responses (001, 002, ...) with sanitized filenames
7. Generate selected outputs

---

## Stage 6 — Output Structure

```
output/
└── SourceName-YYYY-MM-DD-HHMM/
    ├── logs/
    │   ├── navigation.txt
    │   ├── session.json
    │   ├── curls.sh
    │   └── responses/
    │       ├── 001_GET_api_search.json
    │       ├── 002_POST_api_login.json
    │       └── ...
    ├── spider_requests/          ← only if selected
    │   ├── spider.py
    │   └── requirements.txt
    └── spider_playwright/        ← only if selected
        ├── spider.py
        └── requirements.txt
```

### `navigation.txt` format

```
[14:30:01] GET  https://registros.com/                        200
[14:30:02] POST https://registros.com/api/login               302
[14:30:03] --- NOTE: Filling search form ---
[14:30:05] GET  https://registros.com/api/results?q=smith     200
[14:30:06] GET  https://registros.com/api/results?q=smith     200  (repeated x4)
```

### `session.json` format

Array of request objects:
```json
[
  {
    "index": 1,
    "method": "GET",
    "url": "https://registros.com/api/search",
    "request_headers": {},
    "payload": null,
    "status": 200,
    "response_headers": {},
    "timestamp": "2026-08-18T14:30:01",
    "duration_ms": 142,
    "type": "fetch",
    "origin_page": "https://registros.com/",
    "notes": [],
    "excluded": false,
    "parameters": [],
    "repeated": 1,
    "response_file": "logs/responses/001_GET_api_search.json"
  }
]
```

### Generated spider structure (requests / Playwright)

- Imports
- CLI args via `argparse` (one arg per marked parameter)
- Session / browser setup
- One function per annotated flow step (if notes exist)
- Main execution block

---

## Folder Structure (project)

```
SpiderGeneratorPW/
├── main.py                  ← entry point
├── config/
│   └── defaults.py          ← default form values, noise filter patterns
├── ui/
│   ├── config_form.py       ← Tkinter config form
│   └── annotation_panel.py  ← Tkinter annotation panel
├── recorder/
│   ├── browser.py           ← Playwright launch + request interception
│   ├── interceptor.py       ← request/response capture logic
│   └── deduplicator.py      ← deduplication logic
├── processor/
│   ├── filter.py            ← noise filtering
│   ├── builder.py           ← builds session.json, navigation.txt, curls.sh
│   └── parameter_resolver.py
├── generator/
│   ├── base.py              ← shared generation logic
│   ├── requests_gen.py
│   ├── playwright_gen.py
│   └── scrapy_gen.py        ← stub, not active in v1
├── templates/
│   ├── spider_requests.py.j2
│   ├── spider_playwright.py.j2
│   └── spider_scrapy.py.j2  ← stub
├── output/                  ← default output directory
├── requirements.txt
├── PLAN.md
└── CLAUDE.md
```

---

## Out of Scope (v1)

- Debug / diff mode
- Scrapy generation (field reserved, disabled in UI)
- Headless mode
- AI-assisted features (planned as independent module or future project)
- WebSocket capture
- Session injection (cookies, auth headers at startup)
- HAR export

---

## Open Questions

None. Plan is complete pending approval.
