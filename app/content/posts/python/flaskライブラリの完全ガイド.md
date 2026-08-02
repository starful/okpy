---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250814113826.png
date: 2025-08-15
hatena_path: /entry/2025/08/15/105016
slug: flaskライブラリの完全ガイド
summary: Python の flask は、軽量でシンプルな Web アプリケーションを作成するためのミニマリブラウザーです。
title: Flaskライブラリの完全ガイド
---

# Flaskライブラリの完全ガイド

# Python `flask` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250814113826.png)

Python の `flask` は、軽量でシンプルな Web アプリケーションを作成するためのミニマリブラウザーです。

## 1. `flask` ライブラリの概要

* Web API やサービスを手軽に開発可能
* 簡単なルーティング、URL マッピング
* Jinja2 テンプレートエンジンによる HTML レンダリング

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install flask
```

</div>

---

## 2. 主な機能と使用例

### (1) 基本的なルート操作

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, Flask!"

if __name__ == "__main__":
    app.run()
```

</div>

### (2) URL パラメータの受け取り

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
@app.route("/user/<username>")
def show_user(username):
    return f"User: {username}"
```

</div>

### (3) GET と POST の対応

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from flask import request

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return "POST でログイン"
    return "ログインページ"
```

</div>

### (4) HTML レンダリング (Jinja2)

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from flask import render_template

@app.route("/welcome")
def welcome():
    return render_template("welcome.html", name="Flask")
```

</div>

### (5) リダイレクト

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from flask import redirect, url_for

@app.route("/admin")
def admin():
    return redirect(url_for("hello"))
```

</div>

### (6) JSON の返信

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from flask import jsonify

@app.route("/api")
def api():
    return jsonify({"status": "ok", "message": "Flask API"})
```

</div>

### (7) セッション利用

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from flask import session

app.secret_key = "secret"

@app.route("/set")
def set_session():
    session["user"] = "admin"
    return "session set"
```

</div>

### (8) ファイルアップロード

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from flask import request

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    file.save(f"./uploads/{file.filename}")
    return "uploaded"
```

</div>

### (9) フラスコマンド 実行

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
flask --app app run --debug
```

</div>

### (10) プロダクション環境の構築

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Hello from factory"

    return app
```

</div>

---

## 3. Flask の主要機能

| 機能             | 説明                   |
| -------------- | -------------------- |
| ルーティング         | URL によって処理を分岐        |
| テンプレート         | Jinja2 を用いて HTML を編集 |
| API 開発         | RESTful API の構築が容易   |
| session/リダイレクト | ユーザー状態の管理            |
| ファイルアップロード     | POST によるデータ送信        |

---

## まとめ

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250814113621.png)

Flask は、シンプルで高機能な Web アプリを Python で開発したい方に最適です。
開発スピード、簡単なコード構成、API/ページの一括管理を実現し、個人ブログから端末向けサービスまで対応できます 🚀