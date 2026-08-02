---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20260104173741.png
date: 2026-02-18
hatena_path: /entry/2026/02/18/090000
slug: webサイトを自動操作-pythonのpyppeteer-まだ手作業でやってますか
summary: Pyppeteerは、PythonからChrome/Chromiumブラウザを操作できるライブラリです。WebスクレイピングやE2Eテスト、ブラウザ操作の自動化に便利で、JavaScriptが動く動的なWebサイトも簡単に扱えます。
title: "\U0001F916 Webサイトを自動操作！PythonのPyppeteer、まだ手作業でやってますか？"
---

# 🤖 Webサイトを自動操作！PythonのPyppeteer、まだ手作業でやってますか？

![image](https://storage.googleapis.com/ok-project-assets/okpy/20260104173741.png)

📝 **TL;DR**
Pyppeteerは、PythonからChrome/Chromiumブラウザを操作できるライブラリです。WebスクレイピングやE2Eテスト、ブラウザ操作の自動化に便利で、JavaScriptが動く動的なWebサイトも簡単に扱えます。

***

### 1. 🤔 一体Pyppeteerとは何？（核心的な役割と主な使用例）

PythonでWebサイトを自動操作したいと思ったことはありませんか？例えば、ログインして情報を取得したり、ボタンをクリックして次のページに進んだり…。そんな時、普通ならブラウザを開いて手作業で行うところを、Pythonのコードで代わりにやってもらえたら、どれだけ効率的でしょう！

Pyppeteerは、まさにその「Webブラウザの自動操作」を実現してくれる強力なPythonライブラリです。

#### 核心的な役割：ブラウザの「影武者」になる！

Pyppeteerは、まるでブラウザの「影武者」のような存在です。あなたがPythonコードで指示した通りに、実際のChromeやChromiumブラウザを裏側で操作してくれます。

*   **比喩で理解！**
    Imagine you have a very smart robot butler 🤖 for your web browser. You can tell this butler, "Go to this website," "Click this button," "Fill in this form," and "Take a screenshot." The butler then goes and does exactly what you said using a real browser, but you don't even need to see the browser window yourself! That's essentially what Pyppeteer does for your Python scripts.

    Pyppeteerは、あなたが「このウェブサイトに行って」「このボタンをクリックして」「このフォームに情報を入力して」「スクリーンショットを撮って」といった指示をPythonコードで与えると、それを忠実に実行してくれる「賢いロボット執事」のようなものです。そして、この執事は実際のブラウザを裏側で動かしてくれるので、あなたはブラウザの画面を見ている必要すらありません。

    Webサイトの中には、JavaScriptというプログラムで動的にコンテンツが表示されたり、ユーザーの操作に応じて変化したりするものがあります。このような「生きた」Webサイトから情報を取得したい場合、単にHTMLソースコードをダウンロードするだけでは不十分なことがあります。Pyppeteerを使えば、ブラウザが実際にJavaScriptを実行し、レンダリングした後の「完成された」Webページを操作できるため、これらの課題を解決できます。

#### 主な使用例：こんな時に大活躍！✨

Pyppeteerが真価を発揮するのは、以下のような場面です。

1.  **Webスクレイピング (Web Scraping) 🕸️**:
    動的なWebサイトから情報を収集したいときに非常に強力です。例えば、ECサイトの商品情報（価格、レビュー、在庫）、ニュースサイトの記事一覧、SNSの投稿など、JavaScriptによって生成されるコンテンツも、ブラウザが実際に描画した状態を元に取得できます。`requests`ライブラリなどで単純にHTMLを取得するだけでは難しい、ログインが必要なサイトや、クリック操作をしないと表示されない情報も、Pyppeteerなら楽々です。

2.  **WebアプリケーションのE2Eテスト (End-to-End Testing) 🧪**:
    開発したWebアプリケーションが、実際にブラウザ上で意図した通りに動作するかを確認するためのテスト（E2Eテスト）に利用されます。ユーザーが実際に行う操作（例：フォーム入力、ボタンクリック、画面遷移）をコードでシミュレートし、期待通りの結果が得られるかを検証します。これにより、バグの早期発見や品質向上に貢献します。

3.  **ブラウザ操作の自動化 (Browser Automation) 🚀**:
    日々のルーチンワークで、毎回同じようなブラウザ操作を繰り返していませんか？例えば、特定のWebサイトに定期的にアクセスしてレポートをダウンロードする、Webフォームに自動でデータを入力する、といった作業をPyppeteerで自動化できます。これにより、作業時間を大幅に削減し、ヒューマンエラーを防ぐことができます。

Pyppeteerは、これらのタスクをPythonのコードで、より柔軟かつ強力に、そして効率的に実行するための強力なツールなのです。

***

### 2. 💻 インストール方法

Pyppeteerのインストールは、Pythonのパッケージ管理システムである`pip`を使えば非常に簡単です。ターミナル（WindowsならコマンドプロンプトやPowerShell、macOS/Linuxならターミナル）を開いて、以下のコマンドを実行してください。

```bash
pip install pyppeteer
```

このコマンドを実行すると、Pyppeteer本体と、それが動作するために必要なChromiumブラウザ（軽量版Chrome）のダウンロードが行われます。初回実行時には、Chromiumのダウンロードに少し時間がかかる場合があります。

***

### 3. 🛠️ 実際に動作するサンプルコード

Pyppeteerの基本的な使い方を理解するために、まずは「Googleのトップページを開いて、検索ボックスに「Python」と入力し、検索ボタンをクリックして、結果ページのタイトルを取得する」という簡単なサンプルコードを見てみましょう。

```python
import asyncio
from pyppeteer import launch

async def main():
    # 1. ブラウザを起動する
    # headless=True でブラウザ画面を表示せずに実行 (デフォルト)
    # headless=False でブラウザ画面を表示して実行
    browser = await launch(headless=False) 
    
    # 2. 新しいページを開く
    page = await browser.newPage()
    
    # 3. Googleのトップページにアクセスする
    await page.goto('https://www.google.com')
    
    # 4. ページが完全に読み込まれるのを待つ（必要に応じて）
    # await page.waitForNavigation() # ページ遷移が発生した場合に使う
    
    # 5. 検索ボックスのセレクタを指定して、テキストを入力する
    # Googleの検索ボックスは 'textarea[name="q"]' というCSSセレクタで特定できます。
    await page.type('textarea[name="q"]', 'Python')
    
    # 6. Enterキーを押して検索を実行する
    await page.press('textarea[name="q"]', 'Enter')
    
    # 7. 検索結果ページが読み込まれるのを待つ
    # 検索結果が表示されるまで少し待つ（セレクタの出現を待つのがより確実）
    await page.waitForSelector('h3') # 検索結果のタイトルによく使われるh3タグを待つ
    
    # 8. 検索結果ページのタイトルを取得する
    page_title = await page.title()
    print(f"検索結果ページのタイトル: {page_title}")
    
    # 9. スクリーンショットを撮る (任意)
    await page.screenshot(path='google_search_results.png')
    print("スクリーンショットを保存しました: google_search_results.png")
    
    # 10. ブラウザを閉じる
    await browser.close()

# 非同期関数を実行する
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
```

このコードを`pyppeteer_sample.py`のような名前で保存し、Pythonで実行してみてください。ブラウザが起動し、Googleで「Python」と検索し、結果ページのタイトルが出力され、スクリーンショットが保存されるはずです。

***

### 4. 🔍 コードの詳細説明

上記のサンプルコードが、具体的に何をしているのかを、初心者の方にも分かりやすく解説します。

#### `import asyncio` と `from pyppeteer import launch`

```python
import asyncio
from pyppeteer import launch
```

*   **`import asyncio`**: Pyppeteerは非同期処理（async/await）という特別な仕組みで動きます。`asyncio`は、この非同期処理をPythonで扱うための標準ライブラリです。Webサイトの読み込みや操作は時間がかかることがあるため、その間に他の処理を進められるように非同期処理が使われています。
*   **`from pyppeteer import launch`**: Pyppeteerライブラリの中から、ブラウザを起動するための`launch`関数をインポートしています。

#### `async def main():`

```python
async def main():
    # ... ここに処理が続きます ...
```

*   **`async def main():`**: 非同期処理を行う関数は、`async def`という形で定義します。`main`という名前は、プログラムのエントリーポイント（開始地点）としてよく使われる慣習です。

#### ブラウザの起動とページ操作

```python
    # 1. ブラウザを起動する
    browser = await launch(headless=False) 
    
    # 2. 新しいページを開く
    page = await browser.newPage()
    
    # 3. Googleのトップページにアクセスする
    await page.goto('https://www.google.com')
```

*   **`browser = await launch(headless=False)`**:
    *   `launch()`関数で、Chromiumブラウザを起動します。
    *   `headless=False`を指定すると、実際にブラウザのウィンドウが表示されて操作される様子を見ることができます。学習目的ではこちらの方が分かりやすいです。`True`にすると、画面表示なしでバックグラウンドで実行されます（サーバーサイドなどでよく使われます）。
    *   `await`は、非同期処理が終わるのを待つためのキーワードです。ブラウザの起動には時間がかかるため、完了するまでここで待ちます。
    *   起動したブラウザは`browser`変数に格納されます。

*   **`page = await browser.newPage()`**:
    *   起動したブラウザの中に、新しいタブ（ページ）を作成します。
    *   作成されたページは`page`変数に格納されます。この`page`オブジェクトを使って、Webページ上での様々な操作を行います。

*   **`await page.goto('https://www.google.com')`**:
    *   `page.goto()`メソッドで、指定したURLにアクセスします。
    *   この処理が完了するまで（ページが読み込まれるまで）`await`で待ちます。

#### 要素の特定と操作

```python
    # 5. 検索ボックスのセレクタを指定して、テキストを入力する
    await page.type('textarea[name="q"]', 'Python')
    
    # 6. Enterキーを押して検索を実行する
    await page.press('textarea[name="q"]', 'Enter')
    
    # 7. 検索結果ページが読み込まれるのを待つ
    await page.waitForSelector('h3') # 検索結果のタイトルによく使われるh3タグを待つ
```

*   **`await page.type('textarea[name="q"]', 'Python')`**:
    *   `page.type()`メソッドは、指定した要素にテキストを入力します。
    *   第一引数 `'textarea[name="q"]'` は、**CSSセレクタ**と呼ばれるもので、Webページ上の特定の要素を指し示すための「住所」のようなものです。この場合、「`name`属性が`q`である`textarea`タグ」を意味します。Googleの検索ボックスはこのセレクタで特定できます。
    *   第二引数 `'Python'` が、入力したいテキストです。

*   **`await page.press('textarea[name="q"]', 'Enter')`**:
    *   `page.press()`メソッドは、指定した要素でキーボードのキーを押します。
    *   ここでは、検索ボックス（`textarea[name="q"]`）に対して`Enter`キーを押しています。これにより、検索が実行されます。

*   **`await page.waitForSelector('h3')`**:
    *   Webサイトは、JavaScriptによって動的にコンテンツが生成されることがあります。検索結果が表示されるまでには少し時間がかかる場合があります。
    *   `page.waitForSelector()`は、指定したCSSセレクタに一致する要素がページ上に現れるまで待機します。ここでは、検索結果のタイトルがよく`h3`タグで表示されることを利用して、結果が表示され始めたことを確認しています。これにより、検索結果のタイトルを取得する前に、ページが準備できていることを保証します。

#### 情報の取得と終了処理

```python
    # 8. 検索結果ページのタイトルを取得する
    page_title = await page.title()
    print(f"検索結果ページのタイトル: {page_title}")
    
    # 9. スクリーンショットを撮る (任意)
    await page.screenshot(path='google_search_results.png')
    print("スクリーンショットを保存しました: google_search_results.png")
    
    # 10. ブラウザを閉じる
    await browser.close()
```

*   **`page_title = await page.title()`**:
    *   `page.title()`メソッドは、現在のページの`<title>`タグの内容を取得します。
    *   取得したタイトルは`page_title`変数に格納され、`print()`関数でコンソールに出力しています。

*   **`await page.screenshot(path='google_search_results.png')`**:
    *   `page.screenshot()`メソッドで、現在のページのスクリーンショットを撮り、指定したファイルパス（ここでは`google_search_results.png`）に保存します。
    *   これは、Webスクレイピングの結果を確認したり、E2Eテストで画面の様子を記録したりするのに便利です。

*   **`await browser.close()`**:
    *   最後に、`browser.close()`で起動したブラウザを閉じます。
    *   これにより、リソース（メモリなど）が解放されます。

#### 非同期関数の実行部分

```python
# 非同期関数を実行する
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
```

*   **`if __name__ == "__main__":`**: このブロックは、このPythonスクリプトが直接実行された場合にのみ実行されます。他のスクリプトからインポートされた場合は実行されません。
*   **`asyncio.get_event_loop().run_until_complete(main())`**:
    *   `asyncio`のイベントループを取得し、その中で`main()`という非同期関数を実行します。
    *   `run_until_complete()`は、指定した非同期関数が完了するまで、イベントループを動かし続けます。

この一連の流れで、Pyppeteerを使った基本的なWebブラウザ操作が実現できています。

***

### 5. ⚠️ 注意点またはヒント

Pyppeteerを使い始めるときに、初心者がつまずきやすいポイントや、知っておくと便利なヒントを2つご紹介します。

1.  **セレクタの重要性と取得方法 🧐**:
    Pyppeteerで最も頻繁に使うことになるのが「CSSセレクタ」です。`page.type()`や`page.click()`などのメソッドで、どの要素を操作するかを指定するために使います。Google Chromeなどのブラウザには、開発者ツール（F12キーなどで開けます）という便利な機能があり、これを使うとWebページ上の要素のCSSセレクタを簡単に調べることができます。
    *   **ヒント**: 操作したい要素を右クリックし、「検証」または「要素を調査」を選択すると、開発者ツールでその要素のHTMLが表示されます。その要素を右クリックして「Copy」→「Copy selector」を選ぶと、その要素のCSSセレクタがクリップボードにコピーされます。これをPyppeteerのコードに貼り付けて使ってみましょう。ただし、サイトによってはセレクタが頻繁に変わったり、複数要素で同じセレクタが使われたりすることもあるので、注意が必要です。

2.  **非同期処理（async/await）の理解 🧠**:
    Pyppeteerは非同期処理で動作するため、Pythonの`async`と`await`の概念を理解することが重要です。最初は少し難しく感じるかもしれませんが、Webサイトの操作は時間がかかることが多いため、非同期処理によってプログラム全体がブロックされる（止まってしまう）のを防ぎ、効率的に処理を進めることができます。
    *   **ヒント**: サンプルコードの`await`がついている行は、「この処理が終わるまで待ってください」という意味です。`await`がついている関数（`launch`, `newPage`, `goto`, `type`, `waitForSelector`など）は、非同期関数であり、必ず`await`を付けて呼び出す必要があります。また、これらの非同期関数を呼び出す関数自体も`async def`で定義する必要があります。最初は「`await`がついているものは、時間がかかる処理が終わるのを待ってくれるものだ」と覚えておけば大丈夫です。

***

### 6. 🔗 一緒に見ておくと良いライブラリ

Pyppeteerと組み合わせて使うと、さらに強力になるライブラリがいくつかありますが、次の一歩として特におすすめなのは **Pandas** です。

*   **Pandas (パンダス) 📊**:
    Pandasは、Pythonでデータ分析を行うための非常に人気のあるライブラリです。PyppeteerでWebサイトから収集したデータを、PandasのDataFrameという表形式のデータ構造に変換することで、データの整理、加工、集計、可視化などが非常に容易になります。
    例えば、PyppeteerでECサイトから商品名、価格、評価などの情報を集めてきたとします。これらの情報をPandas DataFrameに格納すれば、価格の高い順に並べ替えたり、平均価格を計算したり、CSVファイルとして保存したりといったことが、数行のコードで実現できます。Webスクレイピングで収集したデータを「使える形」にするために、Pandasは欠かせない存在と言えるでしょう。

***

### 7. 🎉 まとめ

今日は、PythonでWebブラウザを自動操作できるライブラリ「Pyppeteer」について学びました。

*   Pyppeteerは、Chrome/ChromiumブラウザをPythonコードから制御し、Webスクレイピング、E2Eテスト、ブラウザ操作の自動化などに活用できます。
*   `pip install pyppeteer`で簡単にインストールでき、`launch`, `newPage`, `goto`, `type`, `waitForSelector`といったメソッドを使ってブラウザ操作を行います。
*   非同期処理（async/await）が使われている点と、CSSセレクタの理解が重要です。

さあ、今日学んだことを活かして、ぜひ次の「挑戦課題」に取り組んでみてください！

#### 🚀 あなたへの挑戦課題！

1.  **「今日の天気」を自動取得**:
    お住まいの地域の天気予報サイト（例: Yahoo!天気、tenki.jpなど）にアクセスし、今日の天気（例: 晴れ、最高気温、最低気温）をPyppeteerで取得して、コンソールに表示させてみましょう。2.  **「Python 入門」でWikipediaを検索**:
    Googleで「Python 入門」と検索し、表示された検索結果の最初の3つの記事のタイトルとURLをPyppeteerで取得し、リスト形式で表示させてみましょう。3.  **収集したデータをCSVに保存**:
    上記の課題で取得した情報を、Pandasを使ってDataFrameに格納し、CSVファイルとして保存する練習をしてみましょう。

これらの課題を通して、Pyppeteerの操作に慣れ、Web自動化の楽しさを体験してみてください！Happy coding! 🎉

***

### 🔖 推奨タグ

#スクレイピング
#Pyppeteer