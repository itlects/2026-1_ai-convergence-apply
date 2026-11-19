import argparse
import json
import re
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parent


def load_data(path):
    return json.loads(path.read_text(encoding="utf-8"))


def tokens(text):
    return set(re.findall(r"[가-힣a-z0-9]+", text.lower()))


def retrieve(question, rows):
    query = tokens(question)
    # 검색 키워드 부분 일치: 한국어 조사에 대한 단순 대응
    scored = []
    for row in rows:
        score = sum(
            any(key in word for word in query)
            for key in row["keywords"]
        )
        scored.append((score, row))
    score, row = max(scored, key=lambda item: item[0])
    if score == 0:
        return {"answer": "자료에서 확인할 수 없습니다.", "source": None, "score": 0}
    return {"answer": row["answer"], "source": row["id"], "score": score}


def make_handler(rows):
    class Handler(BaseHTTPRequestHandler):
        def send_body(self, body, mime, status=200):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/":
                self.send_body((ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
            else:
                self.send_body(b"Not found", "text/plain", 404)

        def do_POST(self):
            if self.path != "/ask":
                self.send_body(b"Not found", "text/plain", 404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    raise ValueError("length")
                payload = json.loads(self.rfile.read(length))
                question = payload["question"]
                if not isinstance(question, str) or not question.strip():
                    raise ValueError("question")
                result = retrieve(question, rows)
                status = 200
            except (ValueError, KeyError, TypeError):
                result = {"error": "질문을 확인하세요."}
                status = 400
            self.send_body(json.dumps(result, ensure_ascii=False).encode(), "application/json; charset=utf-8", status)
    return Handler


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", choices=["campus", "lab"], default="campus")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    rows = load_data(ROOT / f"{args.project}.json")
    print(f"http://127.0.0.1:{args.port} | {args.project}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(rows)).serve_forever()
