#!/usr/bin/env python3
"""Build the static, GitHub Pages-compatible quiz site."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from quizlib import DatasetError, normalize_dataset

ROOT = Path(__file__).resolve().parent
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")


def build(output: Path) -> None:
    """Validate bundled datasets and assemble a self-contained static site."""
    web_dir = ROOT / "web"
    datasets_dir = ROOT / "datasets"
    if not web_dir.is_dir() or not datasets_dir.is_dir():
        raise RuntimeError("The web/ and datasets/ directories are required.")

    output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(web_dir / "index.html", output / "index.html")
    shutil.copy2(web_dir / "app.js", output / "app.js")
    static_dir = output / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "static" / "style.css", static_dir / "style.css")

    published: list[dict[str, object]] = []
    published_dir = output / "datasets"
    published_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(datasets_dir.glob("*.json")):
        if not path.is_file() or not SLUG_RE.fullmatch(path.stem):
            raise ValueError(f"{path.name}: dataset filename is not a valid slug.")
        try:
            dataset = normalize_dataset(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, UnicodeDecodeError, DatasetError) as exc:
            raise ValueError(f"{path.name}: invalid dataset: {exc}") from exc
        (published_dir / path.name).write_text(
            json.dumps(dataset, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        published.append(
            {
                "slug": path.stem,
                "title": dataset["title"],
                "subtitle": dataset["subtitle"],
                "question_count": len(dataset["questions"]),
            }
        )

    published.sort(key=lambda item: (str(item["title"]).casefold(), str(item["slug"])))
    (published_dir / "index.json").write_text(
        json.dumps(published, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the static quiz site.")
    parser.add_argument("--output", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    build(args.output)
    print(f"Static site built in {args.output.resolve()}")


if __name__ == "__main__":
    main()
