---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20251210205900.png
date: 2025-12-26
hatena_path: /entry/2025/12/26/090000
slug: python-tesseract-ocr-画像の中の文字-まだ手で打ち込んでいませんか
summary: Tesseract OCRは、画像ファイル（スキャンした書類や写真など）からテキストを自動で読み取るための強力なオープンソースOCRエンジンです。Pythonのpytesseractライブラリと組み合わせることで、文字認識のプロセスを驚くほど簡単に自動化できます。紙媒体の情報をデジタル化したり、画像内の特定のデータを抽…
title: 'Python Tesseract OCR: 画像の中の文字、まだ手で打ち込んでいませんか？'
---

# Python Tesseract OCR: 画像の中の文字、まだ手で打ち込んでいませんか？

![image](https://storage.googleapis.com/ok-project-assets/okpy/20251210205900.png)

📝 **TL;DR (3行要約)**

Tesseract OCRは、画像ファイル（スキャンした書類や写真など）からテキストを自動で読み取るための強力なオープンソースOCRエンジンです。Pythonの`pytesseract`ライブラリと組み合わせることで、文字認識のプロセスを驚くほど簡単に自動化できます。紙媒体の情報をデジタル化したり、画像内の特定のデータを抽出したりする作業を劇的に効率化します。

***

### 1. 🤔 一体Tesseract OCRとは何？（核心的な役割と主な使用例）

プログラミングの世界には、面倒な作業を自動化してくれる魔法のようなツールがたくさんあります。今回ご紹介する「Tesseract OCR」も、そんな魔法の一つです。

- **核心的な役割: デジタル世界の「魔法のメガネ」** 👓

コンピュータにとって、画像はただの色のついた点（ピクセル）の集まりに過ぎません。そこに「A」という文字が書かれていても、コンピュータにはそれが何なのか理解できません。

ここで登場するのがTesseract OCRです。これは、コンピュータに**画像の中の文字を読む能力を与える「魔法のメガネ」**のようなものだと考えてみてください。このメガネをかけることで、コンピュータは単なるピクセルの集まりの中から文字の形を認識し、それを私たちが普段使っているテキストデータ（例: "Hello, World!"）に変換してくれるのです。

元々はGoogleによって開発・メンテナンスされており、その高い認識精度とオープンソースである手軽さから、世界中の開発者に愛用されています。Pythonからは`pytesseract`というライブラリを通じて、この魔法の力を簡単に借りることができます。

- **主な使用例: こんな場面で大活躍！** ✨

では、この「魔法のメガネ」は具体的にどんな場面で役立つのでしょうか？代表的な例をいくつか見てみましょう。

1.  **紙の書類のデジタル化と整理** 📂
    会議の議事録、大学の講義ノート、山積みの請求書や領収書...。これらをスキャナやスマホで撮影し、Tesseract OCRにかけることで、中のテキストをすべて検索可能なデジタルデータに変換できます。これにより、「あの会議で話したキーワードなんだっけ？」と思った時に、画像ファイルを一つ一つ開くことなく、テキスト検索だけで目的の書類を瞬時に見つけ出せるようになります。経費精算の自動化など、業務効率化の第一歩として非常に強力です。

2.  **街中の情報収集と活用** 🏙️
    旅行先で見かけたレストランの看板、ポスターに書かれたイベント情報、名刺に記載された連絡先など、写真に撮った画像から必要な情報だけを抜き出すことができます。例えば、レストランのメニュー写真を撮って、アレルギー情報を自動でチェックしたり、看板の電話番号を抽出してそのまま電話帳に登録したり、といったアプリケーションが考えられます。

3.  **スクリーンショットからのデータ抽出** 🖥️
    ソフトウェアのテスト中に表示されたエラーメッセージ、Webサイトの特定の箇所の情報、ゲームのスコア画面など、スクリーンショットからテキストを読み取って、ログとして保存したり、分析したりするのに役立ちます。手作業で転記する手間とミスをなくし、作業の自動化を大きく前進させることができます。

このように、Tesseract OCRは「画像」と「テキスト」という異なる世界の架け橋となり、これまで手作業に頼らざるを得なかった多くのタスクを自動化する可能性を秘めているのです。

***

### 2. 💻 インストール方法

Tesseract OCRをPythonで使うには、2つのステップが必要です。

**ステップ1: `pytesseract` ライブラリのインストール**

まずは、PythonからTesseract OCRを操作するためのラッパーライブラリ`pytesseract`と、画像の読み込みに便利な`Pillow`をインストールします。ターミナル（またはコマンドプロンプト）で以下のコマンドを実行してください。

```bash
pip install pytesseract pillow
```

**ステップ2: Tesseract OCRエンジン本体のインストール**

`pytesseract`はあくまで「操縦桿」であり、実際に文字認識を行う「エンジン」本体が別途必要です。お使いのOSに合わせてインストールしてください。

-   **Windows の場合:**
    [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) からインストーラー (`.exe`ファイル) をダウンロードしてインストールします。インストール中に言語パックを選択する画面が出てくるので、`Japanese`（日本語）にもチェックを入れておくことを強くお勧めします。

-   **macOS の場合 (Homebrew使用):**
    ターミナルで以下のコマンドを実行します。

    ```bash
    brew install tesseract
    brew install tesseract-lang # これで全言語パックをインストール
    ```

-   **Linux (Ubuntu/Debian系) の場合:**
    ターミナルで以下のコマンドを実行します。

    ```bash
    sudo apt update
    sudo apt install tesseract-ocr
    sudo apt install tesseract-ocr-jpn # 日本語言語パック
    ```

これで準備は完了です！

***

### 3. 🛠️ 実際に動作するサンプルコード

理論はさておき、実際に動かしてみるのが一番です。
以下のコードは、外部に画像ファイルを用意しなくても、コピー＆ペーストするだけでTesseract OCRの基本的な動作を試せるようになっています。プログラム内で日本語のテキストを含む画像を動的に生成し、それをOCRで読み取ります。

```python
# 必要なライブラリをインポートします
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import sys

# --- Tesseract OCRのパス設定 (Windowsユーザー向け) ---
# もしTesseract OCRの実行ファイルにPATHが通っていない場合、
# 以下の行のコメントを解除し、ご自身の環境に合わせてパスを修正してください。
# 例: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def create_sample_image(text, width=600, height=200):
    """
    指定されたテキストを含むサンプル画像を生成する関数
    """
    # 白い背景の画像を新規作成
    img = Image.new('RGB', (width, height), color = 'white')
    draw = ImageDraw.Draw(img)
    
    # フォントの読み込み (OSによってパスが異なる場合があります)
    # Windows: 'meiryo.ttc' or 'msgothic.ttc'
    # macOS: '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
    # Linux: '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    try:
        # 一般的なOSでの日本語フォントパスを試す
        font_path = "meiryo.ttc" if sys.platform == "win32" else "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
        font = ImageFont.truetype(font_path, size=40)
    except IOError:
        print(f"フォントファイルが見つかりません: {font_path}")
        print("システムに存在する日本語フォントのパスを指定してください。")
        # フォントが見つからない場合はデフォルトフォントで続行
        font = ImageFont.load_default()

    # テキストを描画する位置を計算 (中央揃え)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((width - text_width) / 2, (height - text_height) / 2)
    
    # 画像に黒でテキストを描画
    draw.text(position, text, fill='black', font=font)
    
    return img

def run_ocr_on_image(image_obj):
    """
    与えられた画像オブジェクトに対してOCRを実行し、結果を返す関数
    """
    # image_to_string関数で画像からテキストを抽出
    # lang='jpn' を指定することで、日本語の認識精度が向上します
    try:
        extracted_text = pytesseract.image_to_string(image_obj, lang='jpn')
        return extracted_text
    except pytesseract.TesseractNotFoundError:
        print("="*60)
        print("エラー: Tesseract OCRの実行ファイルが見つかりません。")
        print("Tesseract OCRがシステムにインストールされているか、")
        print("またはPythonスクリプト内でパスが正しく設定されているか確認してください。")
        print("(サンプルコード内の 'Tesseract OCRのパス設定' 部分を参照)")
        print("="*60)
        return None

# --- メインの処理 ---
if __name__ == "__main__":
    # 1. OCRで読み取るためのサンプル画像を生成
    japanese_text = "こんにちは、Pythonの世界！\nTesseract OCRは強力です。"
    sample_image = create_sample_image(japanese_text)
    
    # 生成した画像を一時的に保存して確認したい場合は以下のコメントを解除
    # sample_image.save("sample_image.png")
    # print("サンプル画像 'sample_image.png' を保存しました。")

    print("--- 生成した画像からテキストを読み取ります ---")
    
    # 2. 生成した画像に対してOCRを実行
    result = run_ocr_on_image(sample_image)
    
    # 3. 結果を表示
    if result is not None:
        print("\n[ OCRによる抽出結果 ]")
        print("--------------------")
        print(result)
        print("--------------------")

```

***

### 4. 🔍 コードの詳細説明

上記のサンプルコードは、一見すると少し長く感じるかもしれませんが、やっていることは非常にシンプルです。意味のある塊（チャンク）ごとに見ていきましょう。

-   **チャンク1: ライブラリのインポート**
    ```python
    from PIL import Image, ImageDraw, ImageFont
    import pytesseract
    import sys
    ```
    ここでは、プログラムで使う道具を準備しています。
    -   `PIL` (Pillow) は、Pythonで画像を扱うための定番ライブラリです。`Image`で画像データそのものを、`ImageDraw`で画像に図形や文字を描き込む機能を、`ImageFont`で描画に使うフォントを扱います。
    -   `pytesseract` は、この記事の主役。Tesseract OCRエンジンをPythonから呼び出すためのライブラリです。
    -   `sys` は、OSの種類を判別するためにインポートしています（フォントファイルのパスを切り替えるため）。

-   **チャンク2: サンプル画像の動的生成 (`create_sample_image` 関数)**
    ```python
    def create_sample_image(text, width=600, height=200):
        # ... (中略) ...
        img = Image.new('RGB', (width, height), color = 'white')
        draw = ImageDraw.Draw(img)
        # ... (フォント設定) ...
        draw.text(position, text, fill='black', font=font)
        return img
    ```
    この部分は、OCRを試すための「お題」となる画像をプログラム内で作っています。`Image.new()`で真っ白なキャンバスを用意し、`ImageDraw.Draw()`でそのキャンバスに絵を描くための「筆」を手に入れます。最後に`draw.text()`で、指定された日本語テキストを黒色で描き込んでいます。これにより、皆さんが手元に画像ファイルを用意しなくても、コピペだけでコードが動くようになっています。

-   **チャンク3: Tesseract OCRの実行 (`run_ocr_on_image` 関数)**
    ```python
    def run_ocr_on_image(image_obj):
        # ... (中略) ...
        extracted_text = pytesseract.image_to_string(image_obj, lang='jpn')
        return extracted_text
    ```
    ここがTesseract OCRの心臓部です！
    `pytesseract.image_to_string()` という、たった1行のコードが魔法の正体です。
    -   第1引数には、Pillowで開いた（または生成した）画像オブジェクトを渡します。
    -   `lang='jpn'` という引数が非常に重要です。これはTesseract OCRに対して「これから読み取る画像には日本語が含まれているよ」と教えてあげるための設定です。これを指定しないと、英語として解釈しようとするため、日本語は全く正しく認識されません。英語の画像を読み取る場合は `lang='eng'` とします。

-   **チャンク4: メインの処理**
    ```python
    if __name__ == "__main__":
        japanese_text = "こんにちは、Pythonの世界！\nTesseract OCRは強力です。"
        sample_image = create_sample_image(japanese_text)
        result = run_ocr_on_image(sample_image)
        if result is not None:
            print(result)
    ```
    プログラムが実行されたときに、実際に行われる処理の流れです。
    1.  `create_sample_image` を呼び出して、日本語テキスト入りの画像を生成します。
    2.  生成された画像を `run_ocr_on_image` に渡し、テキストを抽出させます。
    3.  返ってきた結果（抽出されたテキスト）を `print` で画面に表示します。

シンプルですよね？たったこれだけで、画像からテキストを抽出するという高度な処理が実現できてしまうのです。

***

### 5. ⚠️ 注意点またはヒント

Tesseract OCRは非常に強力ですが、初心者がハマりやすいポイントがいくつかあります。これを知っておくだけで、多くのエラーを回避できます。

1.  **罠: Tesseract本体への「PATHが通っていない」エラー** 🚫
    `pytesseract.TesseractNotFoundError: tesseract is not installed or it's not in your PATH`
    このエラーは、`pytesseract`がTesseract OCRエンジン本体をどこから呼び出せばいいのか分からずに発生します。特にWindows環境でよく見られます。
    -   **解決策:** プログラムの冒頭で、Tesseract OCRの実行ファイル (`tesseract.exe`) の場所を明示的に教えてあげましょう。サンプルコードにも記載していますが、以下の1行を`import`文の後に追加し、パスを自分の環境に合わせて修正してください。

        ```python
        # Windowsの例
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        ```
        `r''` は、バックスラッシュをエスケープシーケンスとして解釈しないためのPythonの記法で、Windowsのパスを扱う際に便利です。

2.  **ヒント: 認識精度は「画像の前処理」で劇的に変わる！** 🎨
    「試してみたけど、文字がぐちゃぐちゃに認識される…」そんな時は、Tesseract OCRを責める前に、入力する画像を見直してみましょう。人間が読みやすい画像が、必ずしもTesseract OCRにとって読みやすいとは限りません。
    -   **認識精度を上げるコツ:**
        -   **グレースケール化・二値化:** 画像を白黒の2色に変換すると、文字と背景のコントラストが明確になり、認識精度が向上することが多いです。
        -   **ノイズ除去:** 画像に含まれる不要な点や線を消す処理です。
        -   **傾き補正:** 文字が傾いていると誤認識の原因になります。画像を回転させて水平にします。
        -   **適切な解像度:** 解像度が低すぎると文字が潰れて読めません。一般的に300 DPI以上が推奨されます。

    これらの「前処理」は、後述する`OpenCV`のような画像処理専門のライブラリを使うと効率的に行うことができます。まずは「綺麗な画像を渡すことが大事」という意識を持つだけでも、結果は大きく変わってきます。

***

### 6. 🔗 一緒に見ておくと良いライブラリ

-   **OpenCV (`opencv-python`)**
    Tesseract OCRを本格的に活用するなら、**OpenCV**は避けて通れない最高の相棒です。
    OpenCVは、画像や動画を処理するための機能が詰まった巨大なライブラリで、先ほどの「注意点またはヒント」で述べた**画像の前処理**をすべて行うことができます。

    -   **Tesseract OCRとの連携メリット:**
        1.  OpenCVで画像の傾きを補正し、ノイズを除去し、最適な二値化を施す。
        2.  綺麗になった画像をTesseract OCRに渡す。

    この一手間を加えるだけで、Tesseract OCRの認識精度は驚くほど向上します。スキャンした書類の影を取り除いたり、写真の明るさを調整したりと、応用範囲は無限大です。OCRの精度に悩み始めたら、ぜひOpenCVの学習を始めてみてください。

***

### 7. 🎉 まとめ

お疲れ様でした！今回は、画像からテキストを読み取る魔法のツール「Tesseract OCR」と、それをPythonから操る`pytesseract`ライブラリについて学びました。

-   **今日のまとめ:**
    -   Tesseract OCRは、画像内の文字をテキストデータに変換する強力なエンジンです。
    -   Pythonの`pytesseract`を使えば、たった数行のコードでOCRを実行できます。
    -   `pytesseract`ライブラリとは別に、Tesseract OCRエンジン本体のインストールが必要です。
    -   日本語を認識させるには `lang='jpn'` の指定が不可欠です。
    -   認識精度を上げるには、OpenCVなどを使った「画像の前処理」が非常に重要です。

このライブラリを使えば、あなたのアイデア次第で様々な自動化ツールを作成できます。ぜひ、身の回りの「画像からの文字起こし」作業を効率化してみてください。

-   **挑戦課題:**
    1.  あなたのスマートフォンのカメラで、身の回りにある本の1ページや、お店の看板を撮影してみましょう。その画像ファイルをPCに移し、今回のサンプルコードを少し改造して、テキストを読み取れるか試してみてください。
    2.  PCの画面のスクリーンショット（例えば、Webサイトの記事の一部など）を撮り、その画像からテキストを抽出してみましょう。
    3.  `lang='eng'` に変更して、英語のテキストが書かれた画像を読み取ってみましょう。日本語との精度の違いなどを体感してみてください。

プログラミングは、実際に手を動かして試すことで一番身につきます。今日学んだ知識を元に、ぜひ色々な画像で試行錯誤を楽しんでください！