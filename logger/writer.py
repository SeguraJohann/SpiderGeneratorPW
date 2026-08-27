import os
import re
from datetime import datetime


def write_session(records, config):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source = re.sub(r"[^\w\-]", "_", config["source_name"])
    session_dir = os.path.join(config["output_dir"], f"{timestamp}_{source}")
    responses_dir = os.path.join(session_dir, "responses")
    os.makedirs(responses_dir, exist_ok=True)

    _write_log(records, session_dir)
    _write_responses(records, responses_dir)

    print(f"[logger] session written to {session_dir}")
    return session_dir


def _write_log(records, session_dir):
    lines = []
    for record in records:
        if record.get("type") == "session_note":
            lines.append(f"NOTE: {record['text']}\n")
        elif record.get("excluded"):
            continue
        else:
            lines.append(f"# [{record['index']:03}]\n")
            lines.append(_format_curl(record))
            lines.append(_format_response_meta(record))
            for note in record.get("notes", []):
                lines.append(f"NOTE: {note}\n")
        lines.append("")

    log_path = os.path.join(session_dir, "log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _write_responses(records, responses_dir):
    for record in records:
        if record.get("type") == "session_note":
            continue
        if record.get("excluded"):
            continue
        body = record.get("response_body")
        if not body:
            continue

        url_slug = re.sub(r"[^\w\-]", "_", record["url"].split("//")[-1])[:60]
        filename = f"{record['index']:03}_{record['method']}_{url_slug}.txt"
        path = os.path.join(responses_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"[{record['index']:03}] {record['method']} {record['url']}\n")
            f.write(f"Status: {record['status']}\n")
            f.write("-" * 60 + "\n")
            f.write(body)


def _format_response_meta(record):
    lines = [f"# Response: {record['status']}"]

    headers = record.get("response_headers", {})

    if 300 <= record["status"] < 400:
        location = headers.get("location")
        if location:
            lines.append(f"# Location: {location}")

    cookies = headers.get("set-cookie")
    if cookies:
        for cookie in cookies if isinstance(cookies, list) else [cookies]:
            lines.append(f"# Set-Cookie: {cookie}")

    return "\n".join(lines) + "\n"


def _format_curl(record):
    parts = ["curl"]

    if record["method"] != "GET":
        parts.append(f"-X {record['method']}")

    for key, value in record.get("request_headers", {}).items():
        safe_value = value.replace("'", "'\\''")
        parts.append(f"-H '{key}: {safe_value}'")

    if record.get("payload"):
        safe_payload = record["payload"].replace("'", "'\\''")
        parts.append(f"--data '{safe_payload}'")

    parts.append(f"'{record['url']}'")

    return " \\\n  ".join(parts) + "\n"
