#!/usr/bin/env python3
"""Local quiz server.

Run `python3 app.py`, open the printed URL, choose a dataset, and try the quiz.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import secrets
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlencode, urlparse

from quizlib import (
    SLUG_RE,
    DatasetError,
    list_datasets,
    load_dataset,
    save_dataset,
    score_quiz,
    slug_from_filename,
)

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
STATIC_DIR = ROOT / "static"
MAX_BODY = 2 * 1024 * 1024
QUIZ_PATH = re.compile(r"^/quiz/([a-z0-9][a-z0-9_-]{0,79})$")
RESULT_PATH = re.compile(
    r"^/quiz/([a-z0-9][a-z0-9_-]{0,79})/results/([A-Za-z0-9_-]{8,80})$"
)

RULES_HTML = """
<div class="rules">
  <strong>Exam Scoring System:</strong>
  <ul>
    <li>Each question has multiple statements (at least one is true).</li>
    <li><strong>Full score (1.0 pt)</strong>: Select all true statements and only those.</li>
    <li><strong>Half score (0.5 pt)</strong>: Exactly one mistake (1 missed correct OR 1 chosen incorrect).</li>
    <li><strong>Zero score (0.0 pt)</strong>: Two or more mistakes.</li>
  </ul>
</div>
""".strip()


def text_to_html(value: str) -> str:
    return "<br>\n".join(html.escape(line) for line in value.split("\n"))


def render_template(name: str, mapping: dict[str, str]) -> str:
    text = (TEMPLATES / name).read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        return mapping.get(match.group(1), match.group(0))

    return re.sub(r"%%([A-Z0-9_]+)%%", replace, text)


def render_datasets(items: list[dict], selected: str | None) -> str:
    if not items:
        return (
            '<p class="empty">No datasets yet. Upload a JSON file below, '
            "then come back and try the quiz.</p>"
        )
    chosen = selected if any(item["slug"] == selected for item in items) else items[0]["slug"]
    cards = []
    for item in items:
        subtitle = (
            f'<p class="subtitle">{text_to_html(item["subtitle"])}</p>'
            if item["subtitle"]
            else ""
        )
        count = item["question_count"]
        count_label = "1 question" if count == 1 else f"{count} questions"
        checked = " checked" if item["slug"] == chosen else ""
        cards.append(
            f"""<label class="question-card dataset-card">
  <input type="radio" name="dataset" value="{html.escape(item["slug"])}"{checked} required>
  <span>
    <h2>{text_to_html(item["title"])}</h2>
    {subtitle}
    <p class="meta">{count_label} · {html.escape(item["slug"])}.json</p>
  </span>
</label>"""
        )
    body = "\n".join(cards)
    return f"""<form method="post" action="/start">
  <div class="dataset-list">
    {body}
  </div>
  <div class="btn-container">
    <button type="submit" class="btn btn-submit">Try quiz</button>
  </div>
</form>"""


def render_home(
    items: list[dict],
    problems: list[str],
    *,
    error: str | None = None,
    notice: str | None = None,
    notice_slug: str | None = None,
) -> str:
    if error:
        flash = f'<div class="flash flash-err">{text_to_html(error)}</div>'
    elif notice:
        link = ""
        if notice_slug and SLUG_RE.fullmatch(notice_slug):
            link = f' <a href="/quiz/{notice_slug}">Try this quiz</a>'
        flash = f'<div class="flash flash-ok">{text_to_html(notice)}{link}</div>'
    else:
        flash = ""

    if problems:
        rows = "".join(f"<li>{text_to_html(item)}</li>" for item in problems)
        problems_html = (
            '<div class="flash flash-err"><strong>Some dataset files were skipped.</strong>'
            f"<ul>{rows}</ul></div>"
        )
    else:
        problems_html = ""

    return render_template(
        "home.html",
        {
            "RULES": RULES_HTML,
            "FLASH": flash,
            "PROBLEMS": problems_html,
            "DATASETS": render_datasets(items, notice_slug),
        },
    )


def _badge(points: float, mistakes: int) -> str:
    if points == 1.0:
        css = "score-good"
    elif points == 0.5:
        css = "score-mid"
    else:
        css = "score-bad"
    noun = "mistake" if mistakes == 1 else "mistakes"
    label = f"{points:.1f} / 1.0 pt ({mistakes} {noun})"
    return f'<span class="question-score {css}">{html.escape(label)}</span>'


def render_questions(dataset: dict, graded: dict | None) -> str:
    by_id = {}
    if graded is not None:
        by_id = {item["id"]: item for item in graded["questions"]}
    blocks = []
    for question in dataset["questions"]:
        question_id = str(question["id"])
        result = by_id.get(question_id)
        reveal = result is not None
        chosen = result["selected"] if reveal else set()
        correct = result["correct"] if reveal else set()
        options_html = []
        for option in question["options"]:
            option_id = option["id"]
            selected = option_id in chosen
            is_correct = option_id in correct
            classes = ["option-label"]
            if reveal and is_correct:
                classes.append("correct-opt")
            elif reveal and selected:
                classes.append("wrong-opt")
            checked = " checked" if reveal and selected else ""
            disabled = " disabled" if reveal else ""
            options_html.append(
                f"""<label class="{" ".join(classes)}" id="label-{html.escape(question_id)}-{html.escape(option_id)}">
  <input type="checkbox" name="q-{html.escape(question_id)}" value="{html.escape(option_id)}"{checked}{disabled}>
  <span><strong>{html.escape(option_id)}.</strong> {text_to_html(option["text"])}</span>
</label>"""
            )
        badge = _badge(result["points"], result["mistakes"]) if reveal else ""
        explanation = ""
        if reveal:
            tone = "good" if result["points"] == 1.0 else "neutral"
            explanation = (
                f'<div class="explanation {tone}"><strong>Explanation:</strong> '
                f'{text_to_html(question["explanation"])}</div>'
            )
        blocks.append(
            f"""<article class="question-card" id="card-{html.escape(question_id)}">
  <div class="question-title">
    <span>{text_to_html(question["title"])}</span>
    {badge}
  </div>
  <p class="question-text">{text_to_html(question["text"])}</p>
  <div class="options-list">
    {"".join(options_html)}
  </div>
  {explanation}
</article>"""
        )
    return "\n".join(blocks)


def render_quiz_page(dataset: dict, slug: str, graded: dict | None = None) -> str:
    subtitle_bits = []
    if dataset["subtitle"]:
        subtitle_bits.append(f'<p class="subtitle">{text_to_html(dataset["subtitle"])}</p>')
    subtitle_bits.append(f'<p class="meta">{html.escape(slug)}.json</p>')
    if graded is None:
        banner = ""
        buttons = '<button type="submit" class="btn btn-submit">Submit Test</button>'
        form_open = f'<form id="quizForm" method="post" action="/quiz/{html.escape(slug)}">'
        form_close = "</form>"
    else:
        percent = f"{(graded['total'] / graded['max']) * 100:.1f}" if graded["max"] else "0.0"
        banner = (
            '<div class="score-banner">'
            "<p>Your Final Result</p>"
            f"<h2>{graded['total']:.1f} / {graded['max']}</h2>"
            f'<p class="score-percent">Score: {percent}%</p>'
            "</div>"
        )
        buttons = (
            f'<a class="btn btn-reset" href="/quiz/{html.escape(slug)}">Retake Quiz</a>'
            '<a class="btn btn-secondary" href="/">Change dataset</a>'
        )
        form_open = '<div id="quizForm">'
        form_close = "</div>"
    return render_template(
        "quiz.html",
        {
            "TITLE": text_to_html(dataset["title"]),
            "SUBTITLE_BLOCK": "\n".join(subtitle_bits),
            "RULES": RULES_HTML,
            "BANNER": banner,
            "FORM_OPEN": form_open,
            "FORM_CLOSE": form_close,
            "QUESTIONS": render_questions(dataset, graded),
            "BUTTONS": buttons,
        },
    )


def parse_multipart(body: bytes, content_type: str) -> tuple[dict[str, list[str]], dict[str, tuple[str, bytes]]]:
    match = re.search(r'boundary=(?:"([^"]+)"|([^;\s]+))', content_type)
    if not match:
        raise ValueError("The upload is missing a form boundary.")
    boundary = (match.group(1) or match.group(2)).encode("utf-8", "strict")
    fields: dict[str, list[str]] = {}
    files: dict[str, tuple[str, bytes]] = {}
    for part in body.split(b"--" + boundary)[1:]:
        if part.startswith(b"--"):
            break
        if part.startswith(b"\r\n"):
            part = part[2:]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        header_blob, separator, data = part.partition(b"\r\n\r\n")
        if not separator:
            continue
        disposition = ""
        for line in header_blob.decode("utf-8", "replace").split("\r\n"):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            if key.lower().strip() == "content-disposition":
                disposition = value.strip()
        params: dict[str, str] = {}
        for item in disposition.split(";")[1:]:
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            params[key.strip().lower()] = value
        name = params.get("name")
        if not name:
            continue
        filename = params.get("filename")
        if filename is None:
            fields.setdefault(name, []).append(data.decode("utf-8", "replace"))
        else:
            files[name] = (filename, data)
    return fields, files


def parse_request_body(
    body: bytes, content_type: str
) -> tuple[dict[str, list[str]], dict[str, tuple[str, bytes]]]:
    if content_type.startswith("application/x-www-form-urlencoded"):
        parsed = parse_qs(body.decode("utf-8", "replace"), keep_blank_values=True)
        return parsed, {}
    if content_type.startswith("multipart/form-data"):
        return parse_multipart(body, content_type)
    raise ValueError("That form could not be read.")


def flash_from_query(query: str) -> tuple[str | None, str | None, str | None]:
    params = parse_qs(query)
    error = (params.get("error") or [None])[0]
    added = (params.get("added") or [None])[0]
    replaced = (params.get("replaced") or [None])[0]
    notice = None
    slug = None
    if isinstance(added, str) and SLUG_RE.fullmatch(added):
        slug = added
        notice = f"Saved dataset {added}."
    elif isinstance(replaced, str) and SLUG_RE.fullmatch(replaced):
        slug = replaced
        notice = f"Replaced dataset {replaced}."
    if isinstance(error, str) and error:
        if len(error) > 500:
            error = error[:500] + "…"
        return error, None, slug
    return None, notice, slug


class QuizServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class QuizHandler(BaseHTTPRequestHandler):
    data_dir = ROOT / "datasets"
    results: dict[str, dict] = {}
    results_lock = threading.Lock()

    def log_message(self, fmt: str, *args) -> None:
        if os.environ.get("QUIZ_QUIET") == "1":
            return
        super().log_message(fmt, *args)

    def send_html(self, page: str, status: int = 200) -> None:
        body = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def read_body(self) -> tuple[bytes | None, str | None]:
        raw_length = self.headers.get("Content-Length", "")
        if not raw_length.isdigit():
            return None, "The form was empty."
        length = int(raw_length)
        if length > MAX_BODY:
            return None, "That file is too large (max 2 MB)."
        return self.rfile.read(length), None

    def show_home(
        self,
        *,
        status: int = 200,
        error: str | None = None,
        notice: str | None = None,
        notice_slug: str | None = None,
        query: str = "",
    ) -> None:
        if error is None and notice is None and query:
            error, notice, notice_slug = flash_from_query(query)
        items, problems = list_datasets(self.data_dir)
        page = render_home(
            items,
            problems,
            error=error,
            notice=notice,
            notice_slug=notice_slug,
        )
        self.send_html(page, status=status)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path if parsed.path == "/" else parsed.path.rstrip("/")
        if path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if path.startswith("/static/"):
            self.serve_static(path[len("/static/") :])
            return
        if path == "/":
            self.show_home(query=parsed.query)
            return
        quiz_match = QUIZ_PATH.match(path)
        if quiz_match:
            self.show_quiz(quiz_match.group(1))
            return
        result_match = RESULT_PATH.match(path)
        if result_match:
            self.show_result(result_match.group(1), result_match.group(2))
            return
        self.show_home(status=404, error="That page does not exist.")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path if parsed.path == "/" else parsed.path.rstrip("/")
        try:
            if path == "/upload":
                self.handle_upload()
            elif path == "/start":
                self.handle_start()
            else:
                quiz_match = QUIZ_PATH.match(path)
                if quiz_match:
                    self.handle_submit(quiz_match.group(1))
                else:
                    self.send_error(405)
        except Exception:
            traceback.print_exc()
            self.show_home(status=500, error="Something went wrong while handling that request.")

    def serve_static(self, name: str) -> None:
        if name != "style.css" or "/" in name or "\\" in name:
            self.send_error(404)
            return
        path = STATIC_DIR / name
        if not path.is_file():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/css; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def show_quiz(self, slug: str) -> None:
        dataset = load_dataset(self.data_dir, slug)
        if dataset is None:
            self.show_home(status=404, error=f"No dataset named {slug}.")
            return
        self.send_html(render_quiz_page(dataset, slug))

    def show_result(self, slug: str, token: str) -> None:
        with self.results_lock:
            payload = self.results.get(token)
        if payload is None or payload.get("slug") != slug:
            self.show_home(status=404, error="That result is no longer available. Try the quiz again.")
            return
        self.send_html(render_quiz_page(payload["dataset"], slug, payload["graded"]))

    def read_form(self) -> tuple[dict[str, list[str]], dict[str, tuple[str, bytes]]] | None:
        body, error = self.read_body()
        if error:
            self.redirect("/?" + urlencode({"error": error}))
            return None
        try:
            return parse_request_body(body or b"", self.headers.get("Content-Type", ""))
        except ValueError as exc:
            self.redirect("/?" + urlencode({"error": str(exc)}))
            return None

    def handle_start(self) -> None:
        parsed = self.read_form()
        if parsed is None:
            return
        fields, _files = parsed
        slug = (fields.get("dataset") or [""])[0].strip()
        if load_dataset(self.data_dir, slug) is None:
            self.redirect("/?" + urlencode({"error": "Choose a dataset before trying the quiz."}))
            return
        self.redirect(f"/quiz/{quote(slug)}")

    def handle_submit(self, slug: str) -> None:
        dataset = load_dataset(self.data_dir, slug)
        if dataset is None:
            self.show_home(status=404, error=f"No dataset named {slug}.")
            return
        parsed = self.read_form()
        if parsed is None:
            return
        fields, _files = parsed
        answers = {
            str(question["id"]): fields.get(f"q-{question['id']}", [])
            for question in dataset["questions"]
        }
        graded = score_quiz(dataset, answers)
        token = secrets.token_urlsafe(16)
        with self.results_lock:
            self.results[token] = {"slug": slug, "dataset": dataset, "graded": graded}
            while len(self.results) > 100:
                oldest = next(iter(self.results))
                del self.results[oldest]
        self.redirect(f"/quiz/{quote(slug)}/results/{quote(token)}")

    def handle_upload(self) -> None:
        parsed = self.read_form()
        if parsed is None:
            return
        _fields, files = parsed
        upload = files.get("dataset_file")
        if upload is None or not upload[0]:
            self.redirect("/?" + urlencode({"error": "Choose a JSON file to upload."}))
            return
        filename, content = upload
        slug = slug_from_filename(filename)
        if slug is None:
            self.redirect(
                "/?"
                + urlencode(
                    {"error": "Use a .json file whose name contains letters or numbers."}
                )
            )
            return
        try:
            raw = json.loads(content.decode("utf-8"))
        except UnicodeDecodeError:
            self.redirect("/?" + urlencode({"error": "The file must be UTF-8 text."}))
            return
        except json.JSONDecodeError:
            self.redirect("/?" + urlencode({"error": "Could not read that file as JSON."}))
            return
        try:
            existed = (self.data_dir / f"{slug}.json").is_file()
            save_dataset(self.data_dir, slug, raw)
        except DatasetError as exc:
            message = " ".join(exc.errors[:8])
            if len(exc.errors) > 8:
                message += " …"
            self.redirect("/?" + urlencode({"error": message}))
            return
        flag = "replaced" if existed else "added"
        self.redirect("/?" + urlencode({flag: slug}))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the quiz loader.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    QuizHandler.data_dir.mkdir(parents=True, exist_ok=True)
    server = QuizServer((args.host, args.port), QuizHandler)
    print(f"Quiz loader is running at http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
