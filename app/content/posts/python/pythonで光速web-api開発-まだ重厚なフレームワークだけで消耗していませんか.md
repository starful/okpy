---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20251130082828.png
date: 2025-12-16
hatena_path: /entry/2025/12/16/093000_1
slug: pythonで光速web-api開発-まだ重厚なフレームワークだけで消耗していませんか
summary: Starletteは、Pythonで非常に高速な非同期Webサービスを構築するための、軽量でパワフルなツールキットです。
title: Pythonで光速Web API開発、まだ重厚なフレームワークだけで消耗していませんか？
---

# Pythonで光速Web API開発、まだ重厚なフレームワークだけで消耗していませんか？

![image](https://storage.googleapis.com/ok-project-assets/okpy/20251130082828.png)

📝 **TL;DR (3行要約)**

Starletteは、Pythonで非常に高速な非同期Webサービスを構築するための、軽量でパワフルなツールキットです。
主に、モダンなWebフレームワークであるFastAPIの心臓部として利用されています。
WebSocket、GraphQL、CORSなど、現代的なWeb開発に必要な機能を最小限の構成で提供してくれるのが最大の魅力です。

***

### 1. 🤔 一体Starletteとは何？（核心的な役割と主な使用例）

PythonでWebサイトやAPIを作ろうと思ったとき、多くの人がDjangoやFlaskといった有名なフレームワークを思い浮かべるでしょう。これらは非常に高機能で、いわば「フルコース料理のレシピ付き豪華セット」のようなものです。食材から調理器具、盛り付け方まで、必要なものがほとんど揃っています。

しかし、もしあなたが作りたいのが「特定のスパイスを効かせた絶品のスープ」だけだとしたら、フルコースのセットは少し大げさに感じませんか？

ここで登場するのが**Starlette**です。

- **核心的な役割 🍳**

Starletteを例えるなら、**「プロ仕様の最高級キッチンシステム」**です。

DjangoやFlaskが、前菜からデザートまでのレシピがすべて決まっている「お料理キット」だとすれば、Starletteはピカピカに磨かれた広々とした調理台、超高火力のコンロ、そして基本的な調味料だけが用意されたプロの厨房です。

このキッチンでは、どんな料理を作るかは完全に料理人（つまり、あなた）の自由です。最高のステーキを焼いてもいいし、繊細な和食を作ってもいい。好きな調理器具（ライブラリ）を持ち込んで、自分だけのオリジナル料理（Webアプリケーション）を、最高のパフォーマンスで作り上げることができます。

この「最高のパフォーマンス」を実現しているのが、**ASGI (Asynchronous Server Gateway Interface)** という仕組みです。

少し技術的な話になりますが、従来のWebサーバーの仕組み(WSGI)が「一人の店員さんが、一人のお客様の注文を完全に終えてから次のお客様に対応する」という方式だったのに対し、ASGIは「一人のスーパー店員さんが、複数のお客様の対応を同時に、効率よく切り替えながら進める」ようなイメージです。これにより、待ち時間を大幅に削減し、非常に高速な応答が可能になるのです。Starletteは、このASGIという最新の厨房設備を使いこなすための、最高のツールキットというわけです。

- **主な使用例 🍽️**

この「プロ仕様のキッチン」であるStarletteは、具体的にどのような場面で真価を発揮するのでしょうか。代表的な例を3つ見ていきましょう。

1.  **超高速なマイクロサービスのAPIサーバーとして**
    最近のWeb開発では、一つの巨大なアプリケーションを作るのではなく、「ユーザー認証」「商品検索」「決済」といった小さな機能ごとに独立したサービス（マイクロサービス）を作り、それらを連携させる手法が主流です。
    Starletteは起動が速く、メモリ消費も少ないため、特定の機能に特化した軽量なAPIサーバーをサッと立ち上げるのに最適です。例えば、機械学習モデルの予測結果を返すだけのAPIや、データベースから特定の情報を取得してJSON形式で返すだけのAPIなど、「速さが命」の場面で大活躍します。

2.  **WebSocketを使ったリアルタイム通信アプリケーションの基盤として**
    チャットアプリ、オンラインゲーム、株価のリアルタイム更新など、サーバーとブラウザが常に双方向で通信し続ける必要があるアプリケーションを作りたい場合があります。このような通信にはWebSocketという技術が使われます。
    Starletteは、このWebSocketのサポートが非常に強力です。非同期処理を得意とするStarletteのアーキテクチャは、多数のクライアントと同時に接続を維持し続けるWebSocketアプリケーションと非常に相性が良く、安定したリアルタイム通信の基盤を簡単に構築できます。

3.  **新しいWebフレームワークの「エンジン」として**
    実は、これがStarletteの最も重要な役割かもしれません。Starletteのパワフルで柔軟な設計は、新しいWebフレームワークを作るための土台（エンジン）として非常に優れています。
    その最も有名な例が、今、世界中のPython開発者から絶大な人気を誇る**FastAPI**です。FastAPIは、Starletteの高速なWeb処理能力を心臓部として利用し、その上にデータ検証や自動APIドキュメント生成といった、開発をさらに便利にするための素晴らしい機能を追加しています。Starletteを理解することは、FastAPIがなぜあんなに速くて使いやすいのか、その秘密を解き明かす鍵となるのです。

***

### 2. 💻 インストール方法

Starletteを動かすには、Starlette本体と、ASGIサーバー（非同期アプリケーションを動かすためのWebサーバー）が必要です。最も一般的に使われる`uvicorn`も一緒にインストールしましょう。

ターミナル（WindowsならコマンドプロンプトやPowerShell）で、以下のコマンドを実行するだけです。

```bash
pip install starlette uvicorn[standard]
```
`[standard]` を付けることで、`uvicorn`が推奨する依存ライブラリ（`watchfiles`による自動リロード機能など）も一緒にインストールされ、開発が快適になります。

***

### 3. 🛠️ 実際に動作するサンプルコード

百聞は一見にしかず。実際に動くコードを見てみましょう。
以下のコードを `main.py` という名前で保存してください。これは、ホームページと、ユーザー情報を返すAPIの2つの機能を持つ、小さなWebアプリケーションです。

```python
# main.py
import asyncio
from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route

# --- エンドポイント関数の定義 ---

# 1. ホームページ (HTMLを返す非同期関数)
async def homepage(request):
    """
    ルートURL('/')にアクセスがあった場合に呼ばれる関数。
    簡単なHTMLを生成して返します。
    """
    html_content = """
    <html>
        <head>
            <title>Starlette入門</title>
        </head>
        <body>
            <h1>ようこそ！Starletteの世界へ 🚀</h1>
            <p>これはStarletteで動作しているシンプルなWebページです。</p>
            <p>試してみよう:</p>
            <ul>
                <li><a href="/user/Alice?greet=Hello">アリスさんへの挨拶</a></li>
                <li><a href="/user/Bob?greet=Hi&lang=ja">ボブさんへの挨拶 (日本語)</a></li>
            </ul>
        </body>
    </html>
    """
    return HTMLResponse(html_content)

# 2. ユーザー情報を返すAPI (JSONを返す非同期関数)
async def user_profile(request):
    """
    '/user/{username}' という形式のURLにアクセスがあった場合に呼ばれる関数。
    パスパラメータとクエリパラメータを使って動的なJSONレスポンスを生成します。
    """
    # URLのパスからパラメータを取得 (例: /user/Alice -> 'Alice')
    username = request.path_params['username']

    # URLのクエリ文字列からパラメータを取得 (例: ?greet=Hello -> 'Hello')
    # .get()を使うと、パラメータが存在しない場合にデフォルト値を設定できます。
    greeting = request.query_params.get('greet', 'こんにちは')
    language = request.query_params.get('lang', 'en')

    # 非同期処理のシミュレーション（例: データベースアクセスなど）
    print(f"'{username}'の情報を取得中... (1秒待機)")
    await asyncio.sleep(1)
    print("...情報取得完了！")

    # レスポンスとして返すデータを作成
    response_data = {
        "user": {
            "name": username,
            "language_preference": language
        },
        "message": f"{greeting}, {username}さん！",
        "source": "Starlette API Server"
    }
    
    # Pythonの辞書をJSON形式に変換して返す
    return JSONResponse(response_data)

# --- ルーティングの設定 ---

# URLのパスと、それに対応する関数を紐付けます。
routes = [
    Route("/", endpoint=homepage),
    Route("/user/{username}", endpoint=user_profile),
]

# --- Starletteアプリケーションのインスタンス化 ---

# デバッグモードを有効にし、上記で定義したルーティングを設定します。
app = Starlette(debug=True, routes=routes)

# --- サーバーの起動 (おまけ) ---

# このスクリプトが直接実行された場合にのみUvicornサーバーを起動します。
# 開発時にはターミナルから `uvicorn main:app --reload` を使うのが一般的です。
if __name__ == "__main__":
    import uvicorn
    print("サーバーを起動します... http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

```

この `main.py` を保存したら、ターミナルでそのファイルがあるディレクトリに移動し、以下のコマンドでサーバーを起動します。

```bash
uvicorn main:app --reload
```

- `uvicorn`: ASGIサーバーを起動するコマンドです。
- `main:app`: `main.py` ファイルの中にある `app` という名前の変数（Starletteインスタンス）を実行対象として指定しています。
- `--reload`: ソースコードを保存するたびに、サーバーを自動で再起動してくれる魔法のオプションです。開発中は必ず付けておきましょう。

ターミナルに `Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)` のようなメッセージが表示されたら成功です！
Webブラウザを開いて、 `http://127.0.0.1:8000` にアクセスしてみてください。サンプルコード内のリンクをクリックして、動作を確認してみましょう。

***

### 4. 🔍 コードの詳細説明

さて、先ほどのサンプルコードが何をしているのか、ブロックごとに詳しく見ていきましょう。

#### **1. ライブラリのインポート**

```python
import asyncio
from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.routing import Route
```
ここでは、アプリケーションを構築するために必要な部品をStarletteから取り込んでいます。
- `asyncio`: Pythonの非同期処理を扱うための標準ライブラリです。`await asyncio.sleep(1)` のように、時間のかかる処理をシミュレートするために使っています。
- `Starlette`: アプリケーション本体を作成するための、中心となるクラスです。
- `JSONResponse`, `HTMLResponse`: それぞれ、ブラウザにJSONデータやHTMLコンテンツを返すための便利なクラスです。これらを使うと、適切なHTTPヘッダー（`Content-Type`など）を自動で設定してくれます。
- `Route`: URLのパスと、それを処理する関数（エンドポイント）を紐付けるためのクラスです。

#### **2. エンドポイント関数の定義**

```python
async def homepage(request):
    # ... (処理) ...
    return HTMLResponse(html_content)

async def user_profile(request):
    # ... (処理) ...
    return JSONResponse(response_data)
```
これらは「エンドポイント」や「ビュー関数」と呼ばれるもので、特定のURLにアクセスがあったときに実際に処理を行う心臓部です。
- **`async def`**: Starletteの最大の特徴である「非同期」で関数を定義するためのキーワードです。これにより、重い処理（データベースへの問い合わせや外部APIの呼び出しなど）の待ち時間に、サーバーが別のリクエストを処理できるようになり、全体のパフォーマンスが向上します。
- **`request`引数**: Starletteは、エンドポイント関数を呼び出す際に、現在のHTTPリクエストに関する情報が詰まった`request`オブジェクトを自動的に渡してくれます。
- **パラメータの取得**:
    - `request.path_params['username']`: `/user/Alice` のように、URLのパス自体に含まれる動的な部分（`{username}`）を取得します。
    - `request.query_params.get('greet', ...)`: `/user/Alice?greet=Hello` のように、URLの`?`以降に続く「クエリパラメータ」を取得します。`.get()`メソッドを使うことで、そのパラメータが存在しない場合のデフォルト値を安全に設定できます。
- **`return`**: 関数の最後では、`HTMLResponse`や`JSONResponse`のインスタンスを返します。これにより、Starletteがクライアント（ブラウザなど）に適切な形式でデータを送信します。

#### **3. ルーティングの設定**

```python
routes = [
    Route("/", endpoint=homepage),
    Route("/user/{username}", endpoint=user_profile),
]
```
ここでは、アプリケーションの「交通整理」を行っています。
- `Route`クラスを使って、「どのURLパスにアクセスが来たら、どの関数を呼び出すか」という対応表（リスト）を作成しています。
- `Route("/", ...)` は、サイトのトップページ (`http://...:8000/`) へのアクセスを `homepage` 関数に割り当てています。
- `Route("/user/{username}", ...)` は、`/user/誰かの名前` という形式のパスへのアクセスを `user_profile` 関数に割り当てます。`{username}` の部分はプレースホルダー（場所取り）であり、ここに入力された実際の文字列（`Alice`や`Bob`など）が、`user_profile` 関数内で `request.path_params['username']` として取得できる仕組みです。

#### **4. アプリケーションインスタンスの作成**

```python
app = Starlette(debug=True, routes=routes)
```
これがアプリケーションの本体です。
`Starlette`クラスのインスタンスを作成し、`app`という変数に格納しています。
- `debug=True`: 開発中にエラーが発生した際、ブラウザ上に詳しいデバッグ情報を表示してくれます。これにより、問題の原因究明が非常に楽になります。本番環境では`False`に設定するのが一般的です。
- `routes=routes`: 先ほど作成したルーティング設定を、アプリケーションに適用しています。

この`app`オブジェクトこそが、`uvicorn`が実行するASGIアプリケーションの実体なのです。

***

### 5. ⚠️ 注意点またはヒント

Starletteを使い始める初心者が特に意識しておくと良い点を2つ紹介します。

1.  **罠: Starletteは「フレームワーク」ではなく「ツールキット」である** 🧰
    DjangoやFlaskを使ったことがある人は、データベースを扱うためのORMや、HTMLを生成するためのテンプレートエンジン、ユーザー認証機能などが「最初から入っている」ことに慣れているかもしれません。
    しかし、Starletteはあくまで**ツールキット**です。つまり、基本的なWebサーバー機能は提供しますが、それ以外の機能は付属していません。データベースを使いたければSQLAlchemyやTortoise ORMを、テンプレートエンジンを使いたければJinja2を、自分で選んで組み合わせる必要があります。
    この自由度の高さは中級者以上にとっては大きなメリットですが、初心者にとっては「何を選べばいいか分からない…」という混乱の元になりがちです。Starletteは、**「自分で部品を選んで組み立てるのが好きな人」**向けのツールだと心に留めておきましょう。もし「全部入り」が欲しいのであれば、次に紹介するFastAPIを最初から使うのが近道です。

2.  **ヒント: 「非同期(async/await)」を少しだけ意識する** ⚡
    Starletteのパフォーマンスを最大限に引き出す鍵は、`async`/`await`を使った非同期プログラミングです。難しく考える必要はありません。まずは以下の2つのルールを覚えておきましょう。
    - **ルール1**: I/O処理（ファイル読み書き、ネットワーク通信、データベースアクセスなど）を行う可能性のあるライブラリを使うときは、それが`async`に対応しているか確認する。（例: `requests`の代わりに`httpx`を使うなど）
    - **ルール2**: `async`対応の関数を呼び出すときは、必ず先頭に `await` を付けるのを忘れないこと。
    `await`を付け忘れると、処理が終わるのを待たずに次の行に進んでしまい、予期せぬエラーやバグの原因になります。サンプルコードの `await asyncio.sleep(1)` のように、「待つべき処理」の前には`await`を付ける、ということを意識するだけで、多くの問題を避けることができます。

***

### 6. 🔗 一緒に見ておくと良いライブラリ

**FastAPI**

Starletteを学んだあなたが次に進むべき道は、ほぼ間違いなく**FastAPI**です。

FastAPIは、Starletteという超高性能なエンジンを搭載し、その上に
- **Pydanticによる強力な型ヒントとデータ検証機能**
- **Swagger UI / ReDocによる自動APIドキュメント生成機能**

といった、現代的なAPI開発に不可欠なスーパーチャージャーを追加したフレームワークです。

Starletteで学んだルーティングや非同期関数の書き方は、ほぼそのままFastAPIで通用します。Starletteの知識があれば、FastAPIが内部でどのように動いているのかを深く理解でき、より高度なカスタマイズも可能になります。Starletteがいわば「むき出しのエンジン」だとしたら、FastAPIは「洗練されたボディと快適な内装を備えたスポーツカー」と言えるでしょう。

***

### 7. 🎉 まとめ

今日はお疲れ様でした！Pythonの軽量ASGIツールキットであるStarletteについて学びました。

- **Starletteは、ASGIをベースにした高速・軽量なWebツールキットであること。**
- **プロ仕様のキッチンのように、自由度が高く、必要な部品を自分で組み合わせてアプリケーションを構築すること。**
- **`async def`で非同期関数を定義し、`Route`でURLと関数を紐付けるのが基本的な使い方であること。**
- **FastAPIの基盤技術であり、Starletteを学ぶことはFastAPIの理解を深めることに繋がること。**

これらのポイントを掴めていれば、今日の目標は達成です！

最後に、学んだ知識を定着させるための**挑戦課題**です。ぜひトライしてみてください。

1.  **新しいページを追加してみよう！**: サンプルコードに `/about` という新しいパスを追加し、あなたの自己紹介を返す簡単なHTMLページを作成してみてください。`homepage`関数を参考にすれば、きっとできるはずです。
2.  **APIを拡張してみよう！**: `user_profile`関数を改造し、URLに `?age=25` のようなクエリパラメータを追加できるようにしてみましょう。取得した年齢をレスポンスのJSONに含め、`"age": 25` のように表示されるようにしてください。

この記事が、あなたのPython Web開発の旅の一助となれば幸いです。Happy Coding!