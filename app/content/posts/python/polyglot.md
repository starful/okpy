---
title: '多言語自然言語処理の救世主！Python「Polyglot」徹底実践ガイド'
date: 2026-07-18
category: python
slug: polyglot
summary: '- **Polyglot**は、100以上の言語に対応した、高速かつ軽量な多言語自然言語処理（NLP）ライブラリです。 - 言語検出、トークン化、品詞タグ付け、固有名詞抽出（NER）、感情分析などの強力な機能を、シンプルな一貫したAPIで提供します。 - C++依存ライブラリ（PyICU等）のインストールに若干の…'
lang: ja
---

# 多言語自然言語処理の救世主！Python「Polyglot」徹底実践ガイド

## TL;DR
- **Polyglot**は、100以上の言語に対応した、高速かつ軽量な多言語自然言語処理（NLP）ライブラリです。
- 言語検出、トークン化、品詞タグ付け、固有名詞抽出（NER）、感情分析などの強力な機能を、シンプルな一貫したAPIで提供します。
- C++依存ライブラリ（PyICU等）のインストールに若干のコツが必要ですが、一度構築すればグローバルなテキスト解析において無類の強みを発揮します。

---

## 1. Polyglotとは？概要と特徴

現代のWebアプリケーションやデータ分析において、多言語テキストの処理は避けて通れない課題です。例えば、グローバル展開しているサービスのSNS分析、複数言語で届くカスタマーサポートへの問い合わせ分類、多言語混在環境からのメタデータ抽出などが挙げられます。

こうしたタスクに対して、言語ごとに異なるNLPライブラリ（日本語なら `MeCab` や `spaCy+GiNZA`、英語なら `NLTK` や `spaCy`）を使い分けるのは、コードの複雑化やメンテナンスコストの増大を招きます。

この課題を解決するのが **Polyglot** です。

```
                    +----------------------------------+
                    |             Polyglot             |
                    +----------------------------------+
                                     |
      +-----------------+------------+------------+-----------------+
      |                 |                         |                 |
[言語検出]         [トークン化]               [品詞タグ付け]       [固有名詞抽出]
(196言語)          (165言語)                  (16言語)             (40言語)
```

### Polyglotの主な特徴

1. **圧倒的な多言語サポート**
   言語検出は196言語、トークン化は165言語、固有名詞抽出（NER）は40言語、感情分析は136言語に対応しています。
2. **PyICUおよびPyCLD2による高速動作**
   言語検出エンジンにはGoogleが開発した `Chromium Compact Language Detector 2 (CLD2)` のPythonバインディングである `pycld2` を使用しており、非常に高速かつ正確です。
3. **一貫したインターフェース**
   テキストを入力するだけで、言語の自動判別から各NLPタスク（トークン化、NER、感情分析）の実行までを同一のオブジェクトモデルで行うことができます。
4. **単語埋め込み（Word Embeddings）の内包**
   多くの言語に対して、あらかじめトレーニングされた単語ベクトルが提供されており、セマンティックな分析が容易に行えます。

---

## 2. 動作環境とインストールガイド

Polyglotの唯一にして最大の難所は、**インストールプロセス**にあります。Polyglotは内部で `ICU`（International Components for Unicode）や `CLD2` などのC++ライブラリに依存しているため、Pythonの `pip install` を単純に実行するだけではビルドエラーが発生することがあります。

ここでは、各主要OSにおける確実なセットアップ手順を詳しく解説します。

### 2.1. 前提システムパッケージのインストール

Pythonパッケージをインストールする前に、OSレベルでICUライブラリとその開発用ヘッダーを導入する必要があります。

#### Ubuntu / Debian 系 Linux
```bash
sudo apt-get update
sudo apt-get install -y python3-dev libicu-dev build-essential
```

#### macOS (Homebrewを使用)
macOSではHomebrewを使用して `icu4c` をインストールします。また、コンパイル時にコンパイラがICUのパスを発見できるように環境変数を設定する必要があります。
```bash
brew install icu4c

# 環境変数の設定（インストール完了時の指示に従ってください。以下は一例です）
export LDFLAGS="-L/opt/homebrew/opt/icu4c/lib"
export CPPFLAGS="-I/opt/homebrew/opt/icu4c/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/icu4c/lib/pkgconfig"
```

#### Windows
Windows環境でのC++コンパイルはトラブルが多いため、Unofficial Windows Binaries for Python Extension Packagesなどを利用するか、WSL2（Windows Subsystem for Linux）上のUbuntu環境で動作させることを強く推奨します。

---

### 2.2. Pythonパッケージのインストール

システム側の準備ができたら、仮想環境（venv等）をアクティベートした上で、以下の順序でインストールを行います。

```bash
# 依存するPythonバインディングを個別にインストール
pip install pycld2
pip install pyicu
pip install morfessor

# Polyglot本体のインストール
pip install polyglot
```

> **注意:** `pyicu` のビルドでエラーが発生する場合は、前述の `icu4c` のパス設定（LDFLAGS/CPPFLAGS）が正しく通っているかを確認してください。

---

### 2.3. 言語モデル・データのダウンロード

Polyglotは必要な言語モデルをオンデマンドでダウンロードする仕組みを持っています。これには `polyglot download` コマンドを使用します。

実務でよく使われるモデルパッケージをあらかじめダウンロードしておきましょう。

```bash
# 基本的な言語検出・トークン化に必要なパッケージ
polyglot download embeddings2.ja embeddings2.en
polyglot download pos2.ja pos2.en
polyglot download ner2.ja ner2.en
polyglot download sentiment2.ja sentiment2.en
```

一括でダウンロードしたい場合は、以下のようにコマンドを実行します。
```bash
# コレクション単位でのダウンロード（例: 日本語関連リソース）
polyglot download task:embeddings language:ja
polyglot download task:ner language:ja
```

---

## 3. 【実務で使える】機能別コードサンプル

ここからは、実際のプロジェクトでの活用を想定したコード例を示します。Polyglotの主要な6つの機能を、動くコードとともに解説します。

### 3.1. 超高速な多言語検出 (Language Detection)

Polyglot（内部の `pycld2`）は、入力テキストがどの言語で書かれているかを瞬時に判定します。単一の言語だけでなく、1つの文の中に複数の言語が混在している場合、その構成比率まで算出することができます。

```python
from polyglot.detect import Detector
from polyglot.detect.base import logger as detect_logger

# 不要な警告ログを抑制
detect_logger.setLevel("ERROR")

def analyze_languages(text):
    print(f"--- 解析対象テキスト ---\n{text}\n")
    
    # Detectorオブジェクトの生成
    detector = Detector(text)
    
    # 最も確率の高い言語
    primary_lang = detector.language
    print(f"主要言語: {primary_lang.name} (言語コード: {primary_lang.code})")
    print(f"信頼度: {primary_lang.confidence:.2f}%\n")
    
    # 検出されたすべての言語候補
    print("検出された言語の内訳:")
    for lang in detector.languages:
        print(f"  - {lang.name:<12} ({lang.code}): 一致度 {lang.readbytes/detector.bytes * 100:.1f}%")
    print("=" * 50)

# サンプルデータ1: 日本語と英語の混在
sample_1 = "今日のミーティングは14:00からです。Please make sure to bring your progress report."
analyze_languages(sample_1)

# サンプルデータ2: スペイン語
sample_2 = "Hola, ¿cómo estás? Espero que tengas un excelente día de trabajo."
analyze_languages(sample_2)
```

#### 実行結果のイメージ
```text
--- 解析対象テキスト ---
今日のミーティングは14:00からです。Please make sure to bring your progress report.

主要言語: Japanese (言語コード: ja)
信頼度: 98.00%

検出された言語の内訳:
  - Japanese     (ja): 一致度 64.0%
  - English      (en): 一致度 36.0%
==================================================
--- 解析対象テキスト ---
Hola, ¿cómo estás? Espero que tengas un excelente día de trabajo.

主要言語: Spanish (言語コード: es)
信頼度: 99.00%

検出された言語の内訳:
  - Spanish      (es): 一致度 100.0%
==================================================
```

---

### 3.2. トークン化と文分割 (Tokenization & Sentence Splitting)

Polyglotは、言語特有の境界ルールを理解し、テキストを「文（Sentences）」や「単語（Words / Tokens）」に適切に分割します。日本語のように、スペース区切りがない言語（膠着語）に対してもトークン化が行えます。

```python
from polyglot.text import Text

def tokenize_demonstration():
    # 日本語のサンプル
    ja_text = Text("Polyglotは多言語対応のライブラリです。日本語の解析も簡単に行えます。")
    
    print("【日本語の文割（Sentences）】")
    for i, sentence in enumerate(ja_text.sentences, 1):
        print(f"文 {i}: {sentence}")
        
    print("\n【日本語の単語分割（Words/Tokens）】")
    # 最初の文の単語を展開
    first_sentence = ja_text.sentences[0]
    print(" | ".join(first_sentence.words))
    
    print("\n" + "="*50 + "\n")
    
    # 英語と多言語が交じるケース
    en_text = Text("Dr. Smith arrived at 9:30 a.m. in Tokyo, Japan. He was very excited.")
    print("【英語の文割とトークン化】")
    for i, sentence in enumerate(en_text.sentences, 1):
        print(f"文 {i}: {sentence}")
        print(f"  単語数: {len(sentence.words)}")
        print(f"  単語リスト: {list(sentence.words[:8])}...") # 先頭8単語を表示

if __name__ == "__main__":
    tokenize_demonstration()
```

#### 実行結果のイメージ
```text
【日本語の文割（Sentences）】
文 1: Polyglotは多言語対応のライブラリです。
文 2: 日本語の解析も簡単に行えます。

【日本語の単語分割（Words/Tokens）】
Polyglot | は | 多 | 言語 | 対応 | の | ライブラリ | です | 。

==================================================

【英語の文割とトークン化】
文 1: Dr. Smith arrived at 9:30 a.m. in Tokyo, Japan.
  単語数: 12
  単語リスト: ['Dr.', 'Smith', 'arrived', 'at', '9:30', 'a.m.', 'in', 'Tokyo']...
文 2: He was very excited.
  単語数: 5
  単語リスト: ['He', 'was', 'very', 'excited', '.']...
```

---

### 3.3. 固有名詞抽出 (Named Entity Recognition - NER)

NERは、テキスト中から「人名 (I-PER)」「組織名 (I-ORG)」「地名 (I-LOC)」などの固有名詞を検出する技術です。Polyglotは多くの言語で一貫した分類モデルを持っています。

```python
from polyglot.text import Text

def extract_entities():
    # 英語のテキスト
    raw_text = (
        "Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in Cupertino, California. "
        "The current CEO is Tim Cook, who spoke at the United Nations yesterday."
    )
    
    text = Text(raw_text)
    
    print("--- 検出された固有名詞 (NER) ---")
    # text.entities からエンティティ情報を取得
    for entity in text.entities:
        # entity.tag: エンティティの種類 (I-PER, I-ORG, I-LOC)
        # entity: 単語リスト
        entity_name = " ".join(entity)
        entity_type = entity.tag
        
        # わかりやすい表現にマッピング
        type_mapping = {
            "I-PER": "人物 (PERSON)",
            "I-ORG": "組織 (ORGANIZATION)",
            "I-LOC": "場所・地理 (LOCATION)"
        }
        readable_type = type_mapping.get(entity_type, entity_type)
        
        print(f"- {entity_name:<30} | 種別: {readable_type}")

if __name__ == "__main__":
    extract_entities()
```

#### 実行結果のイメージ
```text
--- 検出された固有名詞 (NER) ---
- Apple Inc.                    | 種別: 組織 (ORGANIZATION)
- Steve Jobs                    | 種別: 人物 (PERSON)
- Steve Wozniak                 | 種別: 人物 (PERSON)
- Ronald Wayne                  | 種別: 人物 (PERSON)
- Cupertino                     | 種別: 場所・地理 (LOCATION)
- California                    | 種別: 場所・地理 (LOCATION)
- Tim Cook                      | 種別: 人物 (PERSON)
- United Nations                | 種別: 組織 (ORGANIZATION)
```

---

### 3.4. 品詞タグ付け (POS Tagging)

品詞タグ付け（Part-of-Speech Tagging）は、各単語が「名詞」「動詞」「形容詞」のいずれであるかを識別します。Polyglotは、Universal Dependencies（UD）に基づいた共通のPOSタグ（17種類）を採用しているため、複数言語を横断して一貫したロジックを組むことができます。

主な共通タグ：
- `NOUN` (名詞), `PROPN` (固有名詞)
- `VERB` (動詞), `ADJ` (形容詞), `ADV` (副詞)
- `ADP` (前置詞/助詞), `PRON` (代名詞), `PUNCT` (句読点)

```python
from polyglot.text import Text

def pos_tagging_comparison():
    # 英語と日本語の比較
    english_text = Text("We are buildling the future of AI technology.")
    japanese_text = Text("私たちは人工知能技術の未来を創っています。")
    
    print("【英語の品詞タグ】")
    for word, tag in english_text.pos_tags:
        print(f"  {word:<12} -> {tag}")
        
    print("\n【日本語の品詞タグ】")
    for word, tag in japanese_text.pos_tags:
        print(f"  {word:<12} -> {tag}")

if __name__ == "__main__":
    pos_tagging_comparison()
```

#### 実行結果のイメージ
```text
【英語の品詞タグ】
  We           -> PRON
  are          -> AUX
  buildling    -> VERB
  the          -> DET
  future       -> NOUN
  of           -> ADP
  AI           -> PROPN
  technology   -> NOUN
  .            -> PUNCT

【日本語の品詞タグ】
  私           -> PRON
  たち         -> NOUN
  は           -> ADP
  人工         -> NOUN
  知能         -> NOUN
  技術         -> NOUN
  の           -> ADP
  未来         -> NOUN
  を           -> ADP
  創っ         -> VERB
  て           -> ADP
  い           -> AUX
  ます         -> AUX
  。           -> PUNCT
```

---

### 3.5. 多言語感情分析 (Sentiment Analysis)

Polyglotは各言語の語彙データベースを参照し、テキスト内の各単語がポジティブであるかネガティブであるかを `-1.0` から `+1.0` の範囲で判定します。

```python
from polyglot.text import Text

def analyze_sentiment():
    comments = [
        "This product is absolutely amazing and helpful! I love it.",
        "The customer service was terrible and very slow. Extremely disappointed.",
        "It was an ordinary experience. Not bad, but not great either."
    ]
    
    for i, comment in enumerate(comments, 1):
        print(f"コメント {i}: \"{comment}\"")
        text = Text(comment)
        
        # 感情極性スコアを単語ごとに評価
        total_score = 0
        sentiment_words = []
        
        for word in text.words:
            # word.polarity はポジティブなら +1, ネガティブなら -1, ニュートラルなら 0 を返します
            pol = word.polarity
            if pol != 0:
                sentiment_words.append(f"{word}({pol:+d})")
                total_score += pol
                
        # 全体としての評価
        overall = "ニュートラル"
        if total_score > 0:
            overall = "ポジティブ (Positive)"
        elif total_score < 0:
            overall = "ネガティブ (Negative)"
            
        print(f"  感情判定: {overall} (総合スコア: {total_score:+d})")
        print(f"  影響を与えた単語: {', '.join(sentiment_words) if sentiment_words else 'なし'}")
        print("-" * 60)

if __name__ == "__main__":
    analyze_sentiment()
```

#### 実行結果のイメージ
```text
コメント 1: "This product is absolutely amazing and helpful! I love it."
  感情判定: ポジティブ (Positive) (総合スコア: +3)
  影響を与えた単語: amazing(+1), helpful(+1), love(+1)
------------------------------------------------------------
コメント 2: "The customer service was terrible and very slow. Extremely disappointed."
  感情判定: ネガティブ (Negative) (総合スコア: -2)
  影響を与えた単語: terrible(-1), disappointed(-1)
------------------------------------------------------------
コメント 3: "It was an ordinary experience. Not bad, but not great either."
  感情判定: ニュートラル (総合スコア: +0)
  影響を与えた単語: bad(-1), great(+1)
------------------------------------------------------------
```

---

### 3.6. 単語の形態素解析・音素変換 (Morfessor & Transliteration)

Polyglotは、言語の「最小の形態素（Morphemes）」への分解を、教師なし学習アルゴリズム（Morfessor）を用いて行います。未知語の多いシステムや造語の分析に役立ちます。また、ラテン文字（アルファベット）圏以外の言語をラテン翻字（Romanization）する機能も有しています。

```python
from polyglot.text import Text

def morpheme_and_transliteration():
    # Morfessorによる形態素分解（特に英語などの複合語の分解に有効）
    word_text = Text("unbelievable internationalization sub-component")
    print("【形態素分解結果】")
    for word in word_text.words:
        # word.morphemes で形態素リストが取得できます
        print(f"  {word:<25} -> {' + '.join(word.morphemes)}")
        
    print("\n" + "="*50 + "\n")
    
    # 翻字（アラビア語やギリシャ語をローマ字表記に変換）
    # ※別途、対象言語の音素変換モデル (transliteration.code) が必要です
    try:
        greek_text = Text("Καλημέρα κόσμε") # ギリシャ語で "Good morning world"
        print("【翻字 (Transliteration) 】")
        print(f"原文: {greek_text}")
        
        # 各単語を翻字
        transliterated_words = [word.transliterate("en") for word in greek_text.words]
        print(f"翻字（ローマ字化）: {' '.join(transliterated_words)}")
    except Exception as e:
        print(f"翻字エラー (モデル未ダウンロードの可能性): {e}")

if __name__ == "__main__":
    morpheme_and_transliteration()
```

#### 実行結果のイメージ
```text
【形態素分解結果】
  unbelievable              -> un + believe + able
  internationalization      -> inter + nation + al + ization
  sub-component             -> sub + - + component

==================================================

【翻字 (Transliteration) 】
原文: Καλημέρα κόσμε
翻字（ローマ字化）: kalimera kosme
```

---

## 4. 実務導入における注意点とベストプラクティス

Polyglotは非常にユニークで優れたライブラリですが、実務（特に商用の大規模本番システム）に組み込む際は、以下の課題についてあらかじめ理解し、対策を講じる必要があります。

### 4.1. C++バイナリ依存による環境可搬性（Portability）の低下

Polyglotは `PyICU` や `pycld2` を利用するため、本番サーバーに配置する際にバイナリの互換性問題が発生しがちです。

**【ベストプラクティス】**
- **Dockerによるコンテナ化**を必須とすべきです。Alpine LinuxはC++ライブラリ（musl / glibc の違いなど）のコンパイルで躓きやすいため、ベースイメージには `python:3.10-slim-bullseye` や `ubuntu` などの **Debian系ベース** を使用することをおすすめします。
- 以下は、Polyglotを動かすための最小限の `Dockerfile` の例です。

```dockerfile
FROM python:3.10-slim-bullseye

# システム依存パッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libicu-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# PyICU等のビルドとパッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# 事前に言語モデルをダウンロード
RUN python -c "import polyglot.downloader; \
    polyglot.downloader.downloader.download('embeddings2.en'); \
    polyglot.downloader.downloader.download('embeddings2.ja')"

COPY . .
CMD ["python", "main.py"]
```

### 4.2. 日本語処理における限界

Polyglotの日本語パーサー（トークナイザー）は、日本語専用に開発された `MeCab` や `Sudachi`、あるいは `GiNZA (spaCy)` と比較すると精度が劣る場合があります。

- **理由:** Polyglotの多くのモデルは、Wikipediaなどのオープンな多言語コーパスから半自動的に学習されたものです。そのため、日本語特有の「敬語表現」や「新語・ネットスラング」のトークン化において、不自然な位置で区切られてしまう現象が発生します。
- **対策:** 
  - システム全体が**多言語対応（英語、中国語、日本語が混在するダッシュボードなど）**である場合は、Polyglotの一括処理によるコードの簡潔さを優先する。
  - **日本語の分析精度がビジネス価値に直結する**タスク（例：国内向けの高精度なレビュー感情分析、日本独自の契約書解析など）では、Polyglotではなく、日本語に特化した形態素解析器（MeCab / Sudachi）を前処理に挟み、言語判別（Language Detection）部分にのみPolyglot（`pycld2`）を採用するなどのハイブリッドアプローチを選択してください。

### 4.3. スレッドセーフティとGIL（グローバルインタプリタロック）

Polyglotの一部機能やC++バインディングは、Pythonのマルチスレッド（`threading` モジュール）環境下での並行処理において、パフォーマンスボトルネックになるか、最悪の場合セグメンテーションフォルトを引き起こすケースがあります。

- **対策:** 大量のテキストファイルを並列に処理したい場合は、スレッドではなく **マルチプロセス（`multiprocessing` モジュールや `ProcessPoolExecutor`）** を利用してください。

---

## 5. FAQ (よくある質問 3選)

### Q1. `PyICU` のインストール時に `Failed building wheel for pyicu` エラーが発生します。

**A1. システムのICUライブラリのパスがPythonのコンパイラに伝わっていません。**
特にmacOS（Homebrew環境）や独自ビルドした環境において頻発します。
以下の解決策を実行してください：

1. システムに `icu` がインストールされているか確認する（`brew list icu4c` や `dpkg -l | grep icu`）。
2. 環境変数を明示的に指定して `pip install` を実行する。

```bash
# macOSの例:
export LDFLAGS="-L/opt/homebrew/opt/icu4c/lib"
export CPPFLAGS="-I/opt/homebrew/opt/icu4c/include"
pip install --no-cache-dir pyicu
```

また、Windows環境では `pip` 経由の直接コンパイルを避け、[Gohlkeの非公式バイナリページ](https://www.lfd.uci.edu/~gohlke/pythonlibs/)（※現在ミラーサイトのみの場合あり）から該当するPythonバージョンの `.whl` ファイルをダウンロードして直接 `pip install pyicu-...whl` するか、おとなしく WSL2 (Ubuntu) に切り替えてください。

---

### Q2. `polyglot download` のサーバーに繋がらない、またはダウンロードが非常に遅いです。

**A2. Polyglotのダウンロードサーバーが一時的に不安定な、あるいはサービス停止している場合があります。またプロキシ環境下でエラーになることがあります。**

この場合、Pythonコード内でプロキシを設定するか、手動で tarball をダウンロードして配置する方法をとります。

**対策1: Pythonコード内で明示的にダウンロードを実行する**
```python
from polyglot.downloader import downloader
# ミラーサイトや特定のパスを指定してダウンロードすることも可能です
downloader.download("embeddings2.en", download_dir="/path/to/your/custom/dir")
```

**対策2: 手動配置**
データファイルの実体は、Polyglotのデータリポジトリ（通常、ユーザーディレクトリの `~/polyglot_data` 以下）に配置されます。エラーログに出力されるURL（または[GitHubのPolyglot関連リポジトリ](https://github.com/aboSamoor/polyglot)）から直接モデルファイル（tar.gzなど）をブラウザ等で取得し、`~/polyglot_data/` 配下の適切なディレクトリ（例: `~/polyglot_data/embeddings2/ja/`）に解凍・配置することで機能します。

---

### Q3. オフライン環境（インターネット接続のない本番サーバー）でも使えますか？

**A3. はい、完全にオフラインで動作可能です。**

Polyglotは一度モデルデータをローカルにダウンロードしてしまえば、外部のAPI（Google Translate APIやOpenAI APIなど）にリクエストを送信することなく、すべての解析をローカルCPUで行います。

**オフライン移行手順:**
1. インターネット接続のある環境で、必要なデータ（`embeddings2`、`ner2` など）をすべてダウンロードします。
2. `~/polyglot_data/`（Windowsの場合は `C:\Users\<ユーザー名>\polyglot_data\`）のフォルダを丸ごと圧縮し、本番サーバーに転送します。
3. 本番サーバーの同じディレクトリ構造に展開します。環境変数 `POLYGLOT_DATA_PATH` を設定することで、読み込み先ディレクトリを任意のパスに変更することも可能です。
```bash
export POLYGLOT_DATA_PATH="/opt/app/resources/polyglot_data"
```

これにより、機密性の高いプライベートデータの解析や、社内クローズドネットワークでのNLPタスクにも安心して適用することができます。

---

## 6. まとめ

Pythonの「**Polyglot**」は、言語ごとに異なるパーサーを使い分ける苦痛から開発者を解放してくれる、非常にパワフルなNLPライブラリです。

- **多言語混在データのパース**
- **100以上の言語に対応した高精度・高速な言語検出**
- **感情分析や固有名詞抽出（NER）の一貫したハンドリング**

これらを、わずか数行の記述で完結できる点が最大の強みです。

初期の環境構築（PyICU関連）におけるトラブルさえ乗り越えれば、その後の開発速度は劇的に向上します。ぜひ、あなたの次期グローバルプロダクトやデータ分析システムにPolyglotを組み込んで、その威力を体感してください！
