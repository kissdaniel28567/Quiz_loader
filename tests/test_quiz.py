import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402
from quizlib import (  # noqa: E402
    DatasetError,
    dataset_path,
    load_dataset,
    save_dataset,
    score_question,
    score_quiz,
    slug_from_filename,
)

os.environ["QUIZ_QUIET"] = "1"


def tiny_dataset(title: str, correct: list[str], explanation: str) -> dict:
    return {
        "title": title,
        "subtitle": "Practice",
        "questions": [
            {
                "id": 1,
                "title": "Question 1",
                "text": f"Statements for {title}.",
                "options": [
                    {"id": "A", "text": "Alpha <true>"},
                    {"id": "B", "text": "Beta"},
                    {"id": "C", "text": "Gamma"},
                ],
                "correct": correct,
                "explanation": explanation,
            }
        ],
    }


class ScoringTests(unittest.TestCase):
    def test_deep_learning_dataset_covers_the_study_guide(self):
        dataset = load_dataset(ROOT / "datasets", "deep_learning_foundations")
        self.assertIsNotNone(dataset)
        self.assertEqual(dataset["title"], "Deep Learning Foundations")
        self.assertEqual(len(dataset["questions"]), 131)
        titles = [question["title"] for question in dataset["questions"]]
        self.assertEqual(len(titles), len(set(titles)))
        for prefix, count in {
            "Core": 7,
            "Tasks": 3,
            "Cholesterol": 24,
            "Scaling": 3,
            "Diagnosis": 13,
            "Losses": 4,
            "MLP": 12,
            "Overfitting": 13,
            "Backprop": 3,
            "NumPy attributes": 8,
            "NumPy slicing": 7,
            "NumPy broadcasting": 4,
            "NumPy reductions": 9,
            "NumPy transforms": 5,
            "NumPy views": 7,
            "NumPy functions": 9,
        }.items():
            self.assertEqual(sum(title.startswith(prefix + ":") for title in titles), count)
        answers = {question["id"]: list(question["correct"]) for question in dataset["questions"]}
        self.assertEqual(score_quiz(dataset, answers)["total"], 131.0)

    def test_bundled_dataset_perfect_score(self):
        dataset = load_dataset(ROOT / "datasets", "theory_test_1")
        self.assertIsNotNone(dataset)
        self.assertEqual(dataset["title"], "Theory Test 1 Practice Exam")
        self.assertEqual(len(dataset["questions"]), 11)
        answers = {question["id"]: list(question["correct"]) for question in dataset["questions"]}
        scored = score_quiz(dataset, answers)
        self.assertEqual(scored["total"], 11.0)

    def test_partial_and_zero_scores(self):
        dataset = load_dataset(ROOT / "datasets", "theory_test_1")
        question = dataset["questions"][0]
        self.assertEqual(question["correct"], ["A", "C"])
        self.assertEqual(score_question(question, ["A"])["points"], 0.5)
        self.assertEqual(score_question(question, ["A", "C", "B"])["points"], 0.5)
        self.assertEqual(score_question(question, ["A", "B"])["points"], 0.0)
        self.assertEqual(score_question(question, [])["points"], 0.0)

    def test_slug_and_path_safety(self):
        self.assertEqual(slug_from_filename("Theory Test 1.json"), "theory_test_1")
        self.assertEqual(slug_from_filename("../../etc/passwd.json"), "passwd")
        self.assertIsNone(slug_from_filename("notes.txt"))
        self.assertIsNone(slug_from_filename(".json"))
        with self.assertRaises(DatasetError):
            dataset_path(Path("/tmp"), "../secrets")

    def test_invalid_dataset_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with self.assertRaises(DatasetError):
                save_dataset(folder, "should-not-write", {"title": "X", "questions": []})
            self.assertFalse((folder / "should-not-write.json").exists())

    def test_answers_are_hidden_before_submit(self):
        dataset = tiny_dataset("Markup", ["A"], "SECRET_EXPLANATION <script>")
        page = app.render_quiz_page(dataset, "markup")
        self.assertNotIn("SECRET_EXPLANATION", page)
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;true&gt;", page)
        self.assertNotIn("correct-opt", page)
        self.assertIn("Validate", page)
        self.assertNotIn(">Next<", page)

    def test_page_shows_one_question(self):
        dataset = tiny_dataset("First", ["A"], "SECRET_ONE")
        dataset["questions"].append(
            {
                "id": 2,
                "title": "Question 2",
                "text": "Statements for the second card.",
                "options": [
                    {"id": "A", "text": "Only this one"},
                    {"id": "B", "text": "Not this one"},
                ],
                "correct": ["A"],
                "explanation": "SECRET_TWO",
            }
        )
        page = app.render_quiz_page(dataset, "sample")
        self.assertIn("Statements for First.", page)
        self.assertNotIn("Statements for the second card.", page)
        self.assertNotIn("SECRET_TWO", page)
        self.assertIn("Question 1 of 2", page)


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.previous_dir = app.QuizHandler.data_dir
        app.QuizHandler.data_dir = cls.tmp
        app.QuizHandler.attempts.clear()
        cls.httpd = app.QuizServer(("127.0.0.1", 0), app.QuizHandler)
        cls.port = cls.httpd.server_address[1]
        cls.base = f"http://127.0.0.1:{cls.port}"
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.thread.join(timeout=5)
        cls.httpd.server_close()
        app.QuizHandler.data_dir = cls.previous_dir
        app.QuizHandler.attempts.clear()
        cls._tmp.cleanup()

    def request(self, path, data=None, headers=None):
        req = urllib.request.Request(self.base + path, data=data, headers=headers or {}, method="POST" if data is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status, response.read().decode(), response.geturl()
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode(), error.geturl()

    def test_switch_dataset_then_score(self):
        save_dataset(self.tmp, "alpha", tiny_dataset("Alpha Quiz", ["A", "B"], "ALPHA_REASON"))
        save_dataset(self.tmp, "beta", tiny_dataset("Beta Quiz", ["C"], "BETA_REASON"))

        status, home, _url = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn("Alpha Quiz", home)
        self.assertIn("Beta Quiz", home)
        self.assertIn("Try quiz", home)

        status, page, final = self.request(
            "/start",
            data=urllib.parse.urlencode({"dataset": "beta"}).encode(),
        )
        self.assertEqual(status, 200)
        self.assertIn("/quiz/beta/play/", final)
        self.assertIn("Beta Quiz", page)
        self.assertNotIn("Alpha Quiz", page)
        self.assertNotIn("BETA_REASON", page)
        self.assertIn(">Validate<", page)
        self.assertNotIn(">Next<", page)
        play = urllib.parse.urlparse(final).path

        status, revealed, revealed_url = self.request(
            play,
            data=urllib.parse.urlencode([("action", "validate"), ("q-1", "C")]).encode(),
        )
        self.assertEqual(status, 200)
        self.assertEqual(urllib.parse.urlparse(revealed_url).path, play)
        self.assertIn("BETA_REASON", revealed)
        self.assertIn("correct-opt", revealed)
        self.assertIn(">Next<", revealed)
        self.assertNotIn(">Validate<", revealed)
        self.assertNotIn("Show only wrong", revealed)

        status, summary, _final = self.request(
            play,
            data=urllib.parse.urlencode([("action", "next")]).encode(),
        )
        self.assertEqual(status, 200)
        self.assertIn("1.0 / 1", summary)
        self.assertIn("Score: 100.0%", summary)
        self.assertIn("Fully correct", summary)
        self.assertIn("Show only wrong", summary)
        self.assertIn('data-perfect="1"', summary)

        _status, _page, half_url = self.request(
            "/start",
            data=urllib.parse.urlencode({"dataset": "alpha"}).encode(),
        )
        alpha_play = urllib.parse.urlparse(half_url).path
        self.request(
            alpha_play,
            data=urllib.parse.urlencode([("action", "validate"), ("q-1", "A")]).encode(),
        )
        status, half, _final = self.request(
            alpha_play,
            data=urllib.parse.urlencode([("action", "next")]).encode(),
        )
        self.assertEqual(status, 200)
        self.assertIn("0.5 / 1", half)
        self.assertIn("ALPHA_REASON", half)
        self.assertIn('data-perfect="0"', half)
        self.assertIn("Half credit", half)

    def test_next_reveals_only_the_following_question(self):
        save_dataset(
            self.tmp,
            "steps",
            {
                "title": "Two step quiz",
                "subtitle": "",
                "questions": [
                    {
                        "id": 1,
                        "title": "Question 1",
                        "text": "First prompt only.",
                        "options": [
                            {"id": "A", "text": "True one"},
                            {"id": "B", "text": "False one"},
                        ],
                        "correct": ["A"],
                        "explanation": "FIRST_REASON",
                    },
                    {
                        "id": 2,
                        "title": "Question 2",
                        "text": "Second prompt only.",
                        "options": [
                            {"id": "A", "text": "True two"},
                            {"id": "B", "text": "False two"},
                        ],
                        "correct": ["B"],
                        "explanation": "SECOND_REASON",
                    },
                ],
            },
        )
        _status, first, final = self.request(
            "/start",
            data=urllib.parse.urlencode({"dataset": "steps"}).encode(),
        )
        play = urllib.parse.urlparse(final).path
        self.assertIn("First prompt only.", first)
        self.assertNotIn("Second prompt only.", first)
        self.assertNotIn("FIRST_REASON", first)
        self.assertIn(">Validate<", first)

        _status, revealed, _url = self.request(
            play,
            data=urllib.parse.urlencode([("action", "validate"), ("q-1", "B")]).encode(),
        )
        self.assertIn("FIRST_REASON", revealed)
        self.assertIn(">Next<", revealed)
        self.assertNotIn("Second prompt only.", revealed)
        self.assertIn('class="question-score score-bad"', revealed)

        _status, second, _url = self.request(
            play,
            data=urllib.parse.urlencode([("action", "next")]).encode(),
        )
        self.assertIn("Second prompt only.", second)
        self.assertNotIn("First prompt only.", second)
        self.assertNotIn("FIRST_REASON", second)
        self.assertNotIn("SECOND_REASON", second)
        self.assertIn(">Validate<", second)
        self.assertIn("Question 2 of 2", second)

        self.request(
            play,
            data=urllib.parse.urlencode([("action", "validate"), ("q-2", "B")]).encode(),
        )
        _status, summary, _url = self.request(
            play,
            data=urllib.parse.urlencode([("action", "next")]).encode(),
        )
        self.assertIn("1.0 / 2", summary)
        self.assertIn("Show only wrong", summary)
        self.assertIn("showWrongOnly", summary)
        self.assertIn('data-perfect="0"', summary)
        self.assertIn('data-perfect="1"', summary)
        self.assertIn("FIRST_REASON", summary)
        self.assertIn("SECOND_REASON", summary)

    def test_upload_then_try(self):
        payload = tiny_dataset("Uploaded Quiz", ["A"], "UPLOADED_REASON")
        raw = json.dumps(payload).encode()
        boundary = "----quizboundary"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="dataset_file"; filename="Uploaded Quiz.json"\r\n'
            "Content-Type: application/json\r\n\r\n"
        ).encode() + raw + f"\r\n--{boundary}--\r\n".encode()
        status, page, _url = self.request(
            "/upload",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        self.assertEqual(status, 200)
        self.assertIn("Saved dataset uploaded_quiz.", page)
        self.assertIn("Uploaded Quiz", page)
        self.assertIn('value="uploaded_quiz" checked', page)
        self.assertTrue((self.tmp / "uploaded_quiz.json").is_file())

        status, quiz, final = self.request(
            "/start",
            data=urllib.parse.urlencode({"dataset": "uploaded_quiz"}).encode(),
        )
        self.assertEqual(status, 200)
        self.assertIn("/quiz/uploaded_quiz/play/", final)
        self.assertIn("Statements for Uploaded Quiz.", quiz)
        self.assertNotIn("UPLOADED_REASON", quiz)
        self.assertIn(">Validate<", quiz)

    def test_invalid_upload_is_rejected(self):
        boundary = "----quizboundary"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="dataset_file"; filename="broken.json"\r\n'
            "Content-Type: application/json\r\n\r\n"
            "not-json\r\n"
            f"--{boundary}--\r\n"
        ).encode()
        status, page, _url = self.request(
            "/upload",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        self.assertEqual(status, 200)
        self.assertIn("Could not read that file as JSON.", page)
        self.assertFalse((self.tmp / "broken.json").exists())


if __name__ == "__main__":
    unittest.main()
