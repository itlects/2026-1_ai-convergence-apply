"""노트북 빌더: 완성본/학생용(빈칸) 두 버전을 같은 원본에서 만든다.

코드 안의 {{정답|빈칸}} 표기 → 완성본은 정답, 학생용은 빈칸으로 바뀐다.
예상 결과(markdown)는 완성본을 실제로 실행한 출력(EXPECTED[cell_id])으로 채운다.
"""
import re
import nbformat

BLANK = re.compile(r"\{\{(.+?)\|(.+?)\}\}")


def fill(src, student):
    return BLANK.sub(lambda m: m.group(2) if student else m.group(1), src)


class Book:
    def __init__(self):
        self.cells = []          # (kind, text, cell_id, expect_mode)

    def md(self, text):
        self.cells.append(("md", text.strip("\n"), None, None))

    def code(self, cid, src, expect="auto", note=""):
        """expect: 'auto'(실행 결과로 채움) | 'none' | 직접 쓴 문자열"""
        self.cells.append(("code", src.strip("\n"), cid, (expect, note)))

    def build(self, student, expected=None, title_suffix=""):
        expected = expected or {}
        nb = nbformat.v4.new_notebook()
        nb.metadata = {"colab": {"provenance": []},
                       "kernelspec": {"name": "python3", "display_name": "Python 3"},
                       "language_info": {"name": "python"}}
        for kind, text, cid, ex in self.cells:
            if kind == "md":
                nb.cells.append(nbformat.v4.new_markdown_cell(text))
                continue
            mode, note = ex
            preview = None
            if mode == "auto" and cid in expected:
                preview = expected[cid].rstrip()
            elif mode not in ("auto", "none"):
                preview = mode.strip("\n")
            if preview:
                head = "**▶ 실행 결과 미리 보기**"
                if note:
                    head += f" — {note}"
                lines = preview.splitlines()
                if len(lines) > 40:
                    lines = lines[:38] + ["...", "(이하 생략)"]
                nb.cells.append(nbformat.v4.new_markdown_cell(
                    head + "\n\n```text\n" + "\n".join(lines) + "\n```"))
            c = nbformat.v4.new_code_cell(fill(text, student))
            c.metadata["id"] = cid
            nb.cells.append(c)
        return nb
