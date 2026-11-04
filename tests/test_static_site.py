import json
import tempfile
import unittest
from pathlib import Path

import build_site


class StaticSiteBuildTests(unittest.TestCase):
    def test_build_publishes_all_validated_datasets_and_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build_site.build(output)

            manifest = json.loads((output / "datasets" / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(
                {item["slug"] for item in manifest},
                {"deep_learning_foundations", "theory_test_1"},
            )
            deep_learning = next(
                item for item in manifest if item["slug"] == "deep_learning_foundations"
            )
            self.assertEqual(deep_learning["question_count"], 131)
            published = json.loads(
                (output / "datasets" / "theory_test_1.json").read_text(encoding="utf-8")
            )
            self.assertEqual(published["title"], "Theory Test 1 Practice Exam")
            self.assertTrue((output / "index.html").is_file())
            self.assertTrue((output / "app.js").is_file())
            self.assertTrue((output / "static" / "style.css").is_file())


if __name__ == "__main__":
    unittest.main()
