import json
import threading
import unittest
from urllib.request import Request, urlopen
from http.server import ThreadingHTTPServer
from server import ROOT, load_data, make_handler, retrieve


class TestProjects(unittest.TestCase):
    def test_retrieval(self):
        for project, examples in [
            ("campus", [("도서관 운영 시간", "C01"), ("대출 연장", "C02"), ("학생식당 점심", "C03"), ("셔틀 버스", "C04")]),
            ("lab", [("DHT11 온도", "L01"), ("LED 저항", "L02"), ("초음파 거리", "L03"), ("카메라 이미지 분류", "L04")]),
        ]:
            rows = load_data(ROOT / f"{project}.json")
            for question, expected in examples:
                self.assertEqual(retrieve(question, rows)["source"], expected)
            self.assertIsNone(retrieve("우주선", rows)["source"])

    def test_http(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(load_data(ROOT / "campus.json")))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            with urlopen(base + "/") as res:
                self.assertIn(b"SpeechRecognition", res.read())
            req = Request(base + "/ask", data=json.dumps({"question": "도서관"}).encode(), headers={"Content-Type": "application/json"})
            with urlopen(req) as res:
                self.assertEqual(json.load(res)["source"], "C01")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
