import re

class SimpleMarkdown:
    def __init__(self, text):
        self.text = text

    def parse(self):
        html = self.text

        # 見出し (#〜)
        html = re.sub(r'^# (.+)$', r'<h1 class="sc">\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2 class="sc2">\1</h2>', html, flags=re.MULTILINE)

        # 強調 (**〜**)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # 斜体 (*〜*)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # インラインコード (`〜`)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        # 段落（空行で区切る）
        html = re.sub(r'(?:\r?\n){2,}', r'</p><p>', html)
        html = f"<p>{html}</p>"

        return html
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/post/<slug>")
def post(slug):
    # ここでMarkdownファイルを読み込む
    with open(f"content/{slug}.md", encoding="utf-8") as f:
        text = f.read()
    parser = SimpleMarkdown(text)
    html = parser.parse()
    return render_template("post.html", content=html)
