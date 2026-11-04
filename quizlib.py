"""Load quiz datasets and score multi-select answers."""

from __future__ import annotations

import json
import re
from pathlib import Path

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
QUESTION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,31}$")
OPTION_ID_RE = re.compile(r"^[A-Za-z0-9]{1,8}$")

MAX_QUESTIONS = 200
MAX_OPTIONS = 30


class DatasetError(ValueError):
    """A dataset file or upload did not match the quiz schema."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def slug_from_filename(filename: str) -> str | None:
    """Turn an uploaded file name into a safe dataset slug."""
    base = filename.replace("\\", "/").split("/")[-1].strip()
    if not base.lower().endswith(".json"):
        return None
    stem = base[:-5].strip().lower().replace(" ", "_").replace(".", "_")
    stem = re.sub(r"[^a-z0-9_-]+", "", stem)
    stem = re.sub(r"_+", "_", stem).strip("-_")
    if not SLUG_RE.fullmatch(stem):
        return None
    return stem


def dataset_path(directory: Path, slug: str) -> Path:
    if not SLUG_RE.fullmatch(slug or ""):
        raise DatasetError(["Invalid dataset name."])
    root = directory.resolve()
    path = (root / f"{slug}.json").resolve()
    if path.parent != root:
        raise DatasetError(["Invalid dataset name."])
    return path


def _identifier(value: object, pattern: re.Pattern[str]) -> str | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        text = str(value)
    elif isinstance(value, str):
        text = value.strip()
    else:
        return None
    if pattern.fullmatch(text):
        return text
    return None


def normalize_dataset(data: object) -> dict:
    """Return a cleaned dataset, or raise DatasetError."""
    if not isinstance(data, dict):
        raise DatasetError(["Dataset must be a JSON object with title and questions."])

    errors: list[str] = []
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append("Title must be a non-empty string.")
        title = ""
    else:
        title = title.strip()

    subtitle = data.get("subtitle", "")
    if subtitle is None:
        subtitle = ""
    if not isinstance(subtitle, str):
        errors.append("Subtitle must be a string.")
        subtitle = ""
    else:
        subtitle = subtitle.strip()

    raw_questions = data.get("questions")
    questions: list[dict] = []
    if not isinstance(raw_questions, list) or not raw_questions:
        errors.append("Questions must be a non-empty list.")
    elif len(raw_questions) > MAX_QUESTIONS:
        errors.append(f"A dataset can contain at most {MAX_QUESTIONS} questions.")
    else:
        seen_ids: set[str] = set()
        for index, raw in enumerate(raw_questions, start=1):
            label = f"Question {index}"
            if not isinstance(raw, dict):
                errors.append(f"{label} must be an object.")
                continue
            question_id = _identifier(raw.get("id", index), QUESTION_ID_RE)
            if question_id is None:
                errors.append(f"{label} has an invalid id.")
                question_id = str(index)
            elif question_id in seen_ids:
                errors.append(f"{label} reuses id {question_id}.")
            seen_ids.add(question_id)

            question_title = raw.get("title")
            question_text = raw.get("text")
            if not isinstance(question_title, str) or not question_title.strip():
                errors.append(f"{label} needs a title.")
                question_title = ""
            if not isinstance(question_text, str) or not question_text.strip():
                errors.append(f"{label} needs text.")
                question_text = ""

            explanation = raw.get("explanation", "")
            if explanation is None:
                explanation = ""
            if not isinstance(explanation, str):
                errors.append(f"{label} explanation must be a string.")
                explanation = ""

            raw_options = raw.get("options")
            options: list[dict] = []
            option_ids: list[str] = []
            if not isinstance(raw_options, list):
                errors.append(f"{label} options must be a list.")
            elif len(raw_options) < 2:
                errors.append(f"{label} needs at least two options.")
            elif len(raw_options) > MAX_OPTIONS:
                errors.append(f"{label} can have at most {MAX_OPTIONS} options.")
            else:
                for option_index, raw_option in enumerate(raw_options, start=1):
                    if not isinstance(raw_option, dict):
                        errors.append(f"{label} option {option_index} must be an object.")
                        continue
                    option_id = _identifier(raw_option.get("id"), OPTION_ID_RE)
                    option_text = raw_option.get("text")
                    if option_id is None:
                        errors.append(f"{label} option {option_index} has an invalid id.")
                        continue
                    if option_id in option_ids:
                        errors.append(f"{label} repeats option {option_id}.")
                        continue
                    if not isinstance(option_text, str) or not option_text.strip():
                        errors.append(f"{label} option {option_id} needs text.")
                        continue
                    option_ids.append(option_id)
                    options.append({"id": option_id, "text": option_text.strip()})

            correct: list[str] = []
            raw_correct = raw.get("correct")
            if not isinstance(raw_correct, list) or not raw_correct:
                errors.append(f"{label} must list at least one correct option.")
            else:
                for entry in raw_correct:
                    correct_id = _identifier(entry, OPTION_ID_RE)
                    if correct_id is None or correct_id not in option_ids:
                        errors.append(f"{label} has a correct id that is not one of its options.")
                        continue
                    if correct_id not in correct:
                        correct.append(correct_id)

            if not errors:
                questions.append(
                    {
                        "id": question_id,
                        "title": question_title.strip(),
                        "text": question_text.strip(),
                        "options": options,
                        "correct": correct,
                        "explanation": explanation.strip(),
                    }
                )

    if errors:
        raise DatasetError(errors)
    return {"title": title, "subtitle": subtitle, "questions": questions}


def list_datasets(directory: Path) -> tuple[list[dict], list[str]]:
    """Return valid dataset summaries and messages for files that were skipped."""
    if not directory.is_dir():
        return [], []

    items: list[dict] = []
    problems: list[str] = []
    for path in sorted(directory.glob("*.json")):
        if not path.is_file():
            continue
        if not SLUG_RE.fullmatch(path.stem):
            problems.append(
                f"{path.name}: rename it using lowercase letters, numbers, hyphens, or underscores."
            )
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            dataset = normalize_dataset(raw)
        except json.JSONDecodeError:
            problems.append(f"{path.name}: not valid JSON.")
            continue
        except DatasetError as exc:
            problems.append(f"{path.name}: {exc.errors[0]}")
            continue
        except OSError:
            problems.append(f"{path.name}: could not be read.")
            continue
        items.append(
            {
                "slug": path.stem,
                "title": dataset["title"],
                "subtitle": dataset["subtitle"],
                "question_count": len(dataset["questions"]),
            }
        )
    items.sort(key=lambda item: (item["title"].casefold(), item["slug"]))
    return items, problems


def load_dataset(directory: Path, slug: str) -> dict | None:
    try:
        path = dataset_path(directory, slug)
    except DatasetError:
        return None
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return normalize_dataset(raw)
    except (OSError, json.JSONDecodeError, DatasetError):
        return None


def save_dataset(directory: Path, slug: str, data: object) -> None:
    dataset = normalize_dataset(data)
    path = dataset_path(directory, slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def score_question(question: dict, selected: list[str] | set[str]) -> dict:
    """Score one question.

    Full marks means every correct option is selected and nothing else is.
    Exactly one mistake (one missed correct option, or one wrong selection)
    scores half a point. Two or more mistakes score zero.
    """
    valid_ids = {option["id"] for option in question["options"]}
    correct = set(question["correct"])
    chosen = {str(item) for item in selected if str(item) in valid_ids}
    mistakes = len(chosen - correct) + len(correct - chosen)
    if mistakes == 0:
        points = 1.0
    elif mistakes == 1:
        points = 0.5
    else:
        points = 0.0
    return {
        "points": points,
        "mistakes": mistakes,
        "selected": chosen,
        "correct": correct,
    }


def score_quiz(dataset: dict, answers: dict[str, list[str]]) -> dict:
    per_question = []
    total = 0.0
    for question in dataset["questions"]:
        question_id = str(question["id"])
        result = score_question(question, answers.get(question_id, []))
        per_question.append({"id": question_id, **result})
        total += result["points"]
    return {
        "total": total,
        "max": len(per_question),
        "questions": per_question,
    }
