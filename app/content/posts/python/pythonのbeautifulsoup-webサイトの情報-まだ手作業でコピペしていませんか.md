---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20251130081938.png
date: 2025-12-09
hatena_path: /entry/2025/12/09/Python%E3%81%AEBeautifulSoup%3A_Web%E3%82%B5%E3%82%A4%E3%83%88%E3%81%AE%E6%83%85%E5%A0%B1%E3%80%81%E3%81%BE%E3%81%A0%E6%89%8B%E4%BD%9C%E6%A5%AD%E3%81%A7%E3%82%B3%E3%83%94%E3%83%9A%E3%81%97%E3%81%A6%E3%81%84%E3%81%BE
slug: pythonのbeautifulsoup-webサイトの情報-まだ手作業でコピペしていませんか
summary: BeautifulSoupは、複雑なWebページ（HTML/XML）の構造を解析するためのPythonライブラリです。
title: 'PythonのBeautifulSoup: Webサイトの情報、まだ手作業でコピペしていませんか？'
---

# PythonのBeautifulSoup: Webサイトの情報、まだ手作業でコピペしていませんか？

![image](https://storage.googleapis.com/ok-project-assets/okpy/20251130081938.png)

📝 **TL;DR (3行要約)**

BeautifulSoupは、複雑なWebページ（HTML/XML）の構造を解析するためのPythonライブラリです。
Webスクレイピングで、特定のニュース記事のタイトルや商品の価格など、欲しい情報だけをピンポイントで抜き出す際に使われます。
ごちゃごちゃしたHTMLコードを、Pythonで簡単に操作できるオブジェクトに変換してくれるのが最大の利点です。

***

### 1. 🤔 一体BeautifulSoupとは何？（核心的な役割と主な使用例）

Pythonを学び始めると、「Webスクレイピング」という言葉を耳にすることがあるでしょう。これは、Webサイトから自動で情報を収集する技術のこと。そのスクレイピングの世界で、多くの開発者に愛されているのが、この「BeautifulSoup」です。

- **核心的な役割 🥣**

突然ですが、Webページのソースコード（HTML）を「**具だくさんのごちゃごちゃしたスープ**」だと想像してみてください。このスープの中には、肉や野菜、パスタなど、色々な具材（情報）が混ざり合っています。あなたが欲しいのは、その中にある「人参（特定のデータ）」だけ。手で探すのは大変ですよね？

ここで登場するのが **BeautifulSoup** です。これは、まるで「**魔法のスプーン**」のようなもの。このスプーンを使えば、スープをかき混ぜることなく、あなたが欲しい「人参」だけを綺麗に、そして簡単かつ正確にすくい取ることができるのです。

つまり、BeautifulSoupの核心的な役割は、**構造化されていないHTML/XMLドキュメントを、プログラムが扱いやすいツリー構造に変換し、目的のデータへ簡単にアクセスする手段を提供すること**にあります。

- **主な使用例 📝**

この「魔法のスプーン」は、具体的にどんな場面で活躍するのでしょうか？代表的な例をいくつか見てみましょう。

1.  **ニュースサイトのヘッドライン収集**:
    毎日更新されるニュースサイトから、最新記事のタイトルとURLを自動で取得し、一覧リストを作成する。手作業で毎日チェックする手間が省けます。

2.  **ECサイトの価格動向調査**:
    Amazonや楽天などのECサイトで、気になる商品の価格を定期的にチェック。価格が設定した金額以下になったら通知する、といったシステムも作れます。

3.  **競合他社の情報収集**:
    競合企業のWebサイトから新製品情報やプレスリリースを定期的に収集し、市場の動向を分析するためのデータを集める、といったビジネス用途でも強力なツールとなります。

このように、手作業では時間のかかる定型的な情報収集を自動化したい、あらゆる場面でBeautifulSoupは真価を発揮します。

***

### 2. 💻 インストール方法

インストールは非常に簡単です。ターミナル（WindowsならコマンドプロンプトやPowerShell）を開いて、以下のコマンドを実行するだけです。

```bash
pip install beautifulsoup4
```

また、BeautifulSoupはHTMLを解析するための「パーサー」というエンジンと一緒に使います。Pythonに標準で入っているパーサーもありますが、より高速で柔軟な`lxml`を一緒にインストールしておくことを強くお勧めします。

```bash
pip install beautifulsoup4 lxml
```

これで準備は完了です！

***

### 3. 🛠️ 実際に動作するサンプルコード

百聞は一見にしかず。まずは実際に動くコードを見てみましょう。
以下のコードは、架空のブログサイトのHTMLから、各記事の「タイトル」と「公開日」を抜き出して表示するものです。このコードをコピーして、`sample.py`のような名前で保存し、実行してみてください。

```python
# 必要なライブラリをインポート
from bs4 import BeautifulSoup

# 解析したいHTMLデータ（今回はWebサイトから取得せず、直接文字列として用意）
html_doc = """
<html>
<head>
    <title>My Fictional Blog</title>
</head>
<body>
    <h1>注目の記事</h1>
    <div id="articles">
        <div class="article">
            <h2>BeautifulSoupの基本</h2>
            <p class="date">公開日: 2023-10-26</p>
            <p>この記事では基本を解説します。</p>
        </div>
        <div class="article">
            <h2>Requestsライブラリとの連携</h2>
            <p class="date">公開日: 2023-10-27</p>
            <p>実際にWebからデータを取得する方法。</p>
        </div>
        <div class="article">
            <h2>実践！データ収集テクニック</h2>
            <p class="date">公開日: 2023-10-28</p>
            <p>集めたデータを活用しよう。</p>
        </div>
    </div>
</body>
</html>
"""

# BeautifulSoupオブジェクトを作成
# 第1引数にHTML文字列、第2引数に使うパーサーを指定
soup = BeautifulSoup(html_doc, 'lxml')

# 全ての記事ブロック（classが"article"のdivタグ）を取得
articles = soup.find_all('div', class_='article')

print("ブログ記事一覧:")
print("--------------------")

# 取得した各記事ブロックから、さらに詳細な情報を抜き出す
for article in articles:
    # 記事の中からh2タグを見つけて、その中のテキストを取得
    title = article.find('h2').text
    
    # 記事の中からclassが"date"のpタグを見つけて、その中のテキストを取得
    date = article.find('p', class_='date').text
    
    # 結果を出力
    print(f"タイトル: {title}")
    print(f"{date}\n")

```

**実行結果:**

```
ブログ記事一覧:
--------------------
タイトル: BeautifulSoupの基本
公開日: 2023-10-26

タイトル: Requestsライブラリとの連携
公開日: 2023-10-27

実践！データ収集テクニック
公開日: 2023-10-28

```

見事にHTMLの中から必要な情報だけを抜き出せましたね！

***

### 4. 🔍 コードの詳細説明

さて、先ほどのサンプルコードが何をしているのか、ステップごとに見ていきましょう。

1.  **HTMLの準備とBeautifulSoupオブジェクトの作成**
    ```python
    from bs4 import BeautifulSoup
    html_doc = """...""" # (HTML文字列)
    soup = BeautifulSoup(html_doc, 'lxml')
    ```
    まず、`bs4`から`BeautifulSoup`をインポートします。今回は練習なので、HTMLコードを`html_doc`という変数に直接入れています。そして、`BeautifulSoup(html_doc, 'lxml')`で、ただの文字列だったHTMLを、BeautifulSoupが解析できるオブジェクト（魔法のスプーンで扱えるスープ）に変換しています。`'lxml'`は先ほどインストールした高速な解析エンジンを使う、という指定です。

2.  **目的の要素をまとめて見つける (`find_all`)**
    ```python
    articles = soup.find_all('div', class_='article')
    ```
    ここがBeautifulSoupの真骨頂です。`soup.find_all(...)`は、指定した条件に合うタグを**すべて**見つけてリストとして返してくれます。ここでは「`div`タグで、かつ`class`属性が`'article'`のもの」を探しています。HTMLを見ると、各記事がこの条件に合致する`div`タグで囲まれているのが分かりますね。
    ※`class`はPythonの予約語（キーワード）なので、属性として指定する際は`class_`とアンダースコアを付けます。

3.  **個々の要素から情報を抜き出す (`find`, `.text`)**
    ```python
    for article in articles:
        title = article.find('h2').text
        date = article.find('p', class_='date').text
        print(...)
    ```
    `find_all`で取得した記事ブロックのリストを、`for`ループで一つずつ処理していきます。
    - `article.find('h2')`: `article`という一つの記事ブロックの中から、`h2`タグを**最初の一つだけ**見つけます。
    - `.text`: 見つけたタグ（例: `<h2>BeautifulSoupの基本</h2>`）から、中のテキスト部分（`BeautifulSoupの基本`）だけを抽出します。
    - `article.find('p', class_='date')`: 同じように、記事ブロックの中から「`p`タグで、かつ`class`が`'date'`のもの」を一つ見つけ、そのテキストを取得しています。

このように、`find_all`で大きな塊を掴み、ループで回しながら`find`で個別の情報を抜き取っていくのが基本的な流れです。

***

### 5. ⚠️ 注意点またはヒント

BeautifulSoupを使い始める初心者が知っておくと、未来の自分を助けることになるヒントを一つだけ紹介します。

- **ヒント: ブラウザの「開発者ツール」は最強の相棒 🤝**

スクレイピングで最も重要なのは、**どのタグに欲しい情報が入っているかを見極めること**です。そのための最強のツールが、Google ChromeやFirefoxに標準で搭載されている「開発者ツール」です。

Webページ上で情報を取得したい箇所を右クリックし、「検証」や「要素を調査」を選択してみてください。すると、画面にHTMLコードが表示され、クリックした部分がどのタグに対応しているかがハイライトされます。

このツールを使えば、`find`や`find_all`で指定すべきタグ名や`class`名、`id`名を正確に知ることができます。コードがうまく動かない時、まず確認すべきは対象サイトのHTML構造です。開発者ツールと睨めっこする時間は、必ずあなたを助けてくれます。

***

### 6. 🔗 一緒に見ておくと良いライブラリ

BeautifulSoupはHTMLを「**解析する**」プロですが、WebサイトからHTMLを「**取得する**」機能はありません。そこで最高のパートナーとなるのが`Requests`ライブラリです。

- **Requests**: Pythonで非常に簡単にHTTPリクエストを送れるライブラリです。
  ```python
  import requests
  
  response = requests.get('https://example.com')
  html_text = response.text # ここでWebページのHTMLが取得できる
  ```

`Requests`でWebサイトからHTMLを取得し、そのHTMLを`BeautifulSoup`に渡して解析する。この2つは、Webスクレイピングにおける「最強コンビ」と言えるでしょう。BeautifulSoupに慣れたら、次はぜひ`Requests`を学んでみてください。

***

### 7. 🎉 まとめ

今日はお疲れ様でした！最後に、BeautifulSoupのポイントを振り返りましょう。

- BeautifulSoupは、複雑なHTMLを解析してくれる「魔法のスプーン」。
- `find_all('タグ名', class_='クラス名')`で欲しい情報の塊をまとめて取得。
- `find('タグ名').text`で個別の情報（テキスト）を抜き出す。
- `Requests`ライブラリと組み合わせることで、実際のWebサイトから情報を収集できる。

これで、あなたもWeb上の情報を自動で収集する第一歩を踏み出しました。

**【挑戦課題】**
さっそく、今日学んだことを使ってみましょう！あなたの好きなニュースサイトやブログのトップページにアクセスし、**記事のタイトルを3つだけ**取得して表示するプログラムを書いてみてください。`Requests`も一緒にインストールして、実際にWebサイトからHTMLを取得するところから挑戦してみると、さらに学びが深まるはずです！

***