import re
import os
from datetime import datetime
posts_storage = {}
class SimpleMarkdown:
    def __init__(self, text):
        self.text = text

    def parse(self):
        lines = self.text.split('\n')
        result = []
        in_code_block = False
        code_block_lang = ''
        code_block_content = []
        in_list = False
        list_items = []

        i = 0
        while i < len(lines):
            line = lines[i]
            
            # コードブロック処理
            if line.startswith('```'):
                if not in_list and list_items:
                    result.append('<ul>')
                    for item in list_items:
                        result.append(f'<li>{self.parse_inline(item)}</li>')
                    result.append('</ul>')
                    in_list = False
                    list_items = []
                    
                if not in_code_block:
                    in_code_block = True
                    code_block_lang = line[3:].strip()
                    code_block_content = []
                else:
                    in_code_block = False
                    lang_attr = f' class="language-{code_block_lang}"' if code_block_lang else ''
                    result.append(f'<pre><code{lang_attr}>{"".join(code_block_content)}</code></pre>')
                    code_block_content = []
                    code_block_lang = ''
                i += 1
                continue
            
            if in_code_block:
                code_block_content.append(self.escape_html(line) + '\n')
                i += 1
                continue
            
            # リスト処理
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                if not in_list:
                    in_list = True
                    list_items = []
                list_items.append(line.strip()[2:])
                i += 1
                continue
            elif in_list:
                result.append('<ul>')
                for item in list_items:
                    result.append(f'<li>{self.parse_inline(item)}</li>')
                result.append('</ul>')
                in_list = False
                list_items = []
            
            # 見出し
            if line.startswith('# '):
                result.append(f'<h1 class="sc">{self.parse_inline(line[2:])}</h1>')
            elif line.startswith('## '):
                result.append(f'<h2 class="sc2">{self.parse_inline(line[3:])}</h2>')
            elif line.startswith('### '):
                result.append(f'<h3>{self.parse_inline(line[4:])}</h3>')
            # 引用
            elif line.startswith('> '):
                result.append(f'<blockquote>{self.parse_inline(line[2:])}</blockquote>')
            # 水平線
            elif line.strip() in ['---', '***', '___']:
                result.append('<hr>')
            # 空行
            elif line.strip() == '':
                if result and not result[-1].endswith('</ul>') and not result[-1].endswith('</pre>'):
                    result.append('<br>')
            # 通常の段落
            else:
                result.append(f'<p>{self.parse_inline(line)}</p>')
            
            i += 1
        
        # リストが閉じられていない場合
        if in_list:
            result.append('<ul>')
            for item in list_items:
                result.append(f'<li>{self.parse_inline(item)}</li>')
            result.append('</ul>')
        
        return ''.join(result)

    def parse_inline(self, text):
        # リンク [text](url)
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        # 画像 ![alt](url)
        text = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1">', text)
        # 強調
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # 斜体
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # インラインコード
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        return text
    
    def escape_html(self, text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

from flask import Flask, render_template
app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/post/<post_id>")
def view_post(post_id):
    return render_template("view_post.html", post_id=post_id)

# API エンドポイント
@app.route("/api/posts", methods=["GET"])
def get_posts():
    posts_list = sorted(posts_storage.values(), key=lambda x: x['timestamp'], reverse=True)
    return jsonify(posts_list)

@app.route("/api/posts/<post_id>", methods=["GET"])
def get_post(post_id):
    if post_id in posts_storage:
        post = posts_storage[post_id]
        parser = SimpleMarkdown(post['content'])
        html_content = parser.parse()
        return jsonify({**post, 'html_content': html_content})
    return jsonify({"error": "Post not found"}), 404

@app.route("/api/posts", methods=["POST"])
def create_post():
    data = request.json
    post_id = f"post_{int(datetime.now().timestamp() * 1000)}"
    
    post = {
        'id': post_id,
        'author': data.get('author', '匿名'),
        'title': data.get('title', '無題'),
        'content': data.get('content', ''),
        'tags': data.get('tags', []),
        'timestamp': int(datetime.now().timestamp() * 1000)
    }
    
    posts_storage[post_id] = post
    return jsonify(post), 201

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)