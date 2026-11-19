import unittest
from rag_server import answer
from server import ROOT, load_data


class TestRAG(unittest.TestCase):
    def test_generation(self):
        rows = load_data(ROOT / "campus.json")
        def fake(question, context, key, model):
            self.assertIn("09시", context)
            return "평일 09시부터 18시까지입니다."
        result = answer("도서관", rows, "dummy", "dummy", fake)
        self.assertEqual(result["mode"], "LLM")
        self.assertEqual(result["source"], "C01")
        self.assertIsNone(answer("우주선", rows, "dummy", "dummy", fake)["source"])

    def test_fallback(self):
        def fail(*args):
            raise OSError("offline")
        result = answer("도서관", load_data(ROOT / "campus.json"), "dummy", "dummy", fail)
        self.assertEqual(result["mode"], "fallback")
        self.assertEqual(result["source"], "C01")


if __name__ == "__main__":
    unittest.main()
