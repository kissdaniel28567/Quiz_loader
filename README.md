# Quiz loader

Practice quizzes in the browser. On the main page, select a dataset and try the quiz one question at a time. Validate shows the solution for the current question and turns into Next. At the end, the summary shows how you did, and Show only wrong hides the questions you got fully correct.

Scoring matches the original exam rules: full credit for an exact selection, half a point for exactly one mistake, and zero after that.

## Run

```bash
python3 app.py
```

Open the URL it prints (http://127.0.0.1:8000 by default). No extra packages are required.

```bash
python3 app.py --port 8080
```

## Datasets

Quizzes are JSON files in `datasets/`. The main page lists every valid file.

- Select one and press **Try quiz**.
- Upload a `.json` file to add a dataset, or upload the same file name to replace it.
- Or copy a file into `datasets/` and refresh the page.

Included sets:

- `datasets/theory_test_1.json` — the original grouped practice exam
- `datasets/deep_learning_foundations.json` — every question from the study guide (Lectures 1–6 and NumPy)

```json
{
  "title": "Sample quiz",
  "subtitle": "Optional description",
  "questions": [
    {
      "id": 1,
      "title": "Question 1",
      "text": "Which statements are true?",
      "options": [
        {"id": "A", "text": "First statement"},
        {"id": "B", "text": "Second statement"}
      ],
      "correct": ["A"],
      "explanation": "A is true because..."
    }
  ]
}
```

Each question needs at least two options and at least one correct option. Correct answers stay on the server until you submit.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
