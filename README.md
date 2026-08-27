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

- `log.txt` — all captured requests as full curls with headers and payload, response status, redirect location, set-cookie headers, and your notes — all interleaved in chronological order.
- `responses/` — one file per request, indexed (`001_GET_example_com.txt`). Stored separately since individual responses can be very large. Access them on demand if the LLM needs to inspect a specific one.

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

1. Fill in the config form (source name, initial URL, browser, output directory, capture scope)
2. Navigate the site in the Playwright browser window
3. Add notes in the annotation panel as you go
4. Click **Finish** — the session directory is created automatically

## Project structure

```
config/         Constants and defaults
recorder/       Playwright browser session and HTTP interceptor
ui/             Config form and annotation panel (Tkinter)
logger/         Session directory and log file writer
processor/      Reserved
generator/      Reserved (spider auto-generation — future bonus feature)
```
