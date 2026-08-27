# SpiderGeneratorPW

A tool to facilitate maintenance of existing web scrapers (spiders). Records browser navigation sessions and produces structured, LLM-ready logs to help diagnose and fix broken spiders.

## What it does

When a spider breaks, the usual workflow is:
1. Recreate the broken navigation manually in a browser
2. Copy curls and responses from devtools
3. Add personal notes about what happened at each step
4. Pass the log + notes + broken spider to an LLM to find and fix the discrepancy

This tool automates the recording step. You navigate the site in a real browser while the tool captures every HTTP request as a full curl, lets you add notes inline, and writes a clean log file ready to paste into an LLM.

## Output

Each session creates a directory: `{output_dir}/{timestamp}_{source_name}/`

- `log.txt` — all captured requests as full curls with headers and payload, each preceded by an index (`# [001]`). After each curl: response status, redirect location for 3xx, set-cookie headers. Your notes (per-request and session notes) are interleaved in chronological order.
- `responses/` — one file per request, indexed to match the log (`001_GET_example_com.txt`). Stored separately since individual responses can be very large. Access them on demand if the LLM needs to inspect a specific one.

## Supported spider types

- Scrapy
- Playwright
- Basic (requests + BeautifulSoup)

## Requirements

- Python 3.8+
- See `requirements.txt`

```bash
pip install -r requirements.txt
playwright install
```

## Usage

```bash
python main.py
```

1. Fill in the config form (source name, initial URL, browser, output directory)
2. Optionally configure capture scope, domain scope, noise filter, and response body mode in Advanced settings
3. Navigate the site in the Playwright browser window (opens maximized)
4. Add notes in the annotation panel as you go — per-request notes or free-form session notes
5. Mark any requests you want to exclude from the log using the Exclude button
6. Click **Finish** — the session directory is written automatically

## Config options

| Option | Description |
|---|---|
| Capture scope | Fetch/XHR, Document, Script (JS), or All |
| Domain scope | Main domain only, or include subdomains |
| Filter noise | Skip analytics, tracking, and CDN requests |
| Save response body | Common text types (JSON, HTML, XML) or all text content |
| User agent | Custom user agent string |

## Project structure

```
config/         Constants and defaults
recorder/       Playwright browser session and HTTP interceptor
ui/             Config form and annotation panel (Tkinter)
logger/         Session directory and log file writer
processor/      Reserved
generator/      Reserved (spider auto-generation — future bonus feature)
```
