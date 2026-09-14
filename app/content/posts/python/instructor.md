---
title: 'Python の instructor ライブラリで LLM 出力を型安全に構造化する実践ガイド'
date: 2026-09-14
category: python
slug: instructor
summary: '- `instructor` は OpenAI・Anthropic などの LLM API 呼び出しに Pydantic モデルを組み合わせ、JSON パースやバリデーションの失敗を自動リトライしてくれるライブラリです - `response_model` に Pydantic クラスを渡すだけで、LLM の返答…'
lang: ja
---

# Python の instructor ライブラリで LLM 出力を型安全に構造化する実践ガイド

## TL;DR

- `instructor` は OpenAI・Anthropic などの LLM API 呼び出しに Pydantic モデルを組み合わせ、JSON パースやバリデーションの失敗を自動リトライしてくれるライブラリです
- `response_model` に Pydantic クラスを渡すだけで、LLM の返答をそのまま型付きオブジェクトとして受け取れるため、後続処理でのパースエラーやフィールド欠落に悩まされにくくなります
- バリデーションエラー時の再質問（リトライ）ロジックが組み込まれているため、プロンプトエンジニアリングだけでは防ぎきれない出力の揺れを吸収できます

## 概要

LLM を使ったアプリケーション開発では、「モデルにJSON形式で返してもらう」という要件が頻繁に出てきます。しかし実際にやってみると、

- 説明文が前後に付いてJSONとして`json.loads`できない
- キー名が微妙に違う
- 数値のはずが文字列で返ってくる
- 必須フィールドが抜け落ちる

といった問題に必ずといっていいほど遭遇します。`instructor` はこの「構造化出力」の問題を、Pydantic のバリデーション機構と LLM API のリトライを組み合わせて解決するために作られたライブラリです。

内部的には OpenAI の Function Calling / Tool Calling（Anthropic の Tool Use も同様）を使い、Pydantic モデルのスキーマを LLM に渡してツール呼び出しの形で構造化データを生成させます。バリデーションに失敗した場合は、エラーメッセージを LLM にフィードバックして再生成させる仕組みが標準で組み込まれているため、開発者は「型を定義する」ことに集中できます。

対応しているプロバイダは OpenAI、Anthropic、Google Gemini、Cohere、Mistral、Ollama（ローカルLLM）など幅広く、ほぼ共通のインターフェースで利用できるのも大きな特徴です。

## インストール

pip でインストールします。OpenAI を使う場合は追加の依存は不要ですが、Anthropic を使う場合は extras を指定します。

```bash
# 基本（OpenAI利用時）
pip install instructor

# Anthropic を使う場合
pip install "instructor[anthropic]"

# Google Gemini を使う場合
pip install "instructor[google-generativeai]"
```

API キーは各プロバイダの環境変数（例: `OPENAI_API_KEY`、`ANTHROPIC_API_KEY`）に設定しておきます。

```bash
export OPENAI_API_KEY="sk-..."
```

## 基本サンプル

まずは最もシンプルな例です。ユーザー情報を抽出するタスクを考えます。

```python
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI

# OpenAI クライアントを instructor でパッチする
client = instructor.from_openai(OpenAI())

class UserInfo(BaseModel):
    name: str = Field(description="ユーザーの氏名")
    age: int = Field(description="ユーザーの年齢")
    email: str | None = Field(default=None, description="メールアドレス（不明ならNone）")

user = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=UserInfo,
    messages=[
        {
            "role": "user",
            "content": "田中太郎さんは32歳で、連絡先はtanaka@example.comです。",
        },
    ],
)

print(user)
# UserInfo(name='田中太郎', age=32, email='tanaka@example.com')
print(type(user))  # <class '__main__.UserInfo'>
```

ポイントは `response_model=UserInfo` を渡すだけで、戻り値が生の文字列ではなく `UserInfo` インスタンスになることです。`user.age` は最初から `int` 型として扱えます。

### ネストしたモデルとリストの抽出

実務では単純な1件のオブジェクトではなく、リストやネスト構造を抽出したいケースが多くあります。

```python
from pydantic import BaseModel, Field

class LineItem(BaseModel):
    item_name: str = Field(description="商品名")
    quantity: int = Field(description="数量")
    unit_price: float = Field(description="単価（円）")

class Invoice(BaseModel):
    invoice_number: str
    customer_name: str
    items: list[LineItem]
    total_amount: float = Field(description="合計金額（円）")

invoice = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=Invoice,
    messages=[
        {
            "role": "user",
            "content": """
以下の請求書テキストから情報を抽出してください。

請求書番号: INV-2026-0914
顧客名: 株式会社サンプル
明細:
- ノートPC x2 個 150,000円
- マウス x5 個 2,000円
合計: 310,000円
""",
        },
    ],
)

for item in invoice.items:
    print(f"{item.item_name}: {item.quantity}個 x {item.unit_price}円")
print(f"合計: {invoice.total_amount}円")
```

このように、ネストした Pydantic モデルやリストもそのまま定義でき、LLM 側がそれに沿ったツール呼び出し引数を生成します。

### バリデーションと自動リトライ

`instructor` の真価は、Pydantic のバリデータと組み合わせたときに発揮されます。バリデーションに失敗すると、LLM に「なぜ失敗したか」を伝えて再生成させます。

```python
from pydantic import BaseModel, field_validator

class Review(BaseModel):
    score: int
    comment: str

    @field_validator("score")
    @classmethod
    def score_must_be_valid(cls, v: int) -> int:
        if not (1 <= v <= 5):
            raise ValueError("score は 1〜5 の整数でなければなりません")
        return v

review = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=Review,
    max_retries=3,  # バリデーション失敗時に最大3回まで再生成
    messages=[
        {"role": "user", "content": "このレストランはとても美味しかった。星10段階で評価して。"},
    ],
)

print(review)
```

`max_retries` を指定しておくと、LLM が誤って範囲外の値（例えば10段階評価の値）を返しても、バリデーションエラーを LLM にフィードバックしたうえで自動的に再試行してくれます。これによりプロンプト側で細かい制約を書き切らなくても、Pydantic 側の型・バリデーションルールが最終防衛ラインとして機能します。

### 部分的なストリーミング出力

チャットUIなどでレスポンスを逐次表示したい場合、`Partial` を使うと途中経過のオブジェクトをストリーミングで受け取れます。

```python
from instructor import Partial

class Article(BaseModel):
    title: str
    summary: str
    tags: list[str]

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=Partial[Article],
    stream=True,
    messages=[
        {"role": "user", "content": "Pythonの非同期処理についての記事案を考えて"},
    ],
)

for partial in stream:
    print(partial)  # フィールドが徐々に埋まっていく途中経過のオブジェクト
```

### 非同期での利用

FastAPI などの非同期アプリケーションに組み込む場合は、`AsyncOpenAI` をパッチして利用します。

```python
import asyncio
from openai import AsyncOpenAI
import instructor

async_client = instructor.from_openai(AsyncOpenAI())

async def extract_user(text: str) -> UserInfo:
    return await async_client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=UserInfo,
        messages=[{"role": "user", "content": text}],
    )

result = asyncio.run(extract_user("佐藤花子さんは28歳です。"))
print(result)
```

## 注意点

実務で使う際に押さえておきたい点をまとめます。

1. **トークン消費が増える傾向がある**
   ツール呼び出し用のスキーマ定義がプロンプトに含まれるため、通常のチャット補完よりも入力トークンが増加します。また `max_retries` を設定すると失敗時に追加のAPI呼び出しが発生し、コストとレイテンシが増える点に注意してください。本番運用では `max_retries` の上限を適切に設定し、無限にリトライしないようにしましょう。

2. **モデルによって Tool Calling の精度が異なる**
   GPT-4系やClaude系の高性能モデルでは構造化出力の精度が高い一方、小型モデルや一部のオープンモデルでは複雑なネスト構造やEnumの扱いが不安定になることがあります。本番導入前に実際に使うモデルで十分に検証してください。

3. **バリデータの中で外部I/Oを行わない**
   `field_validator` は同期的に何度も呼ばれる可能性があるため、DBアクセスやAPIコールなど重い処理・副作用のある処理を入れるべきではありません。あくまで値の整合性チェックに留めましょう。

4. **`response_model` のフィールドには必ず `description` を書く**
   `Field(description=...)` はLLMに渡されるスキーマの説明文として使われます。これを省略すると抽出精度が落ちることがあるため、抽出したい内容をフィールドごとに明示するのがコツです。

5. **バージョンによってAPIが変わることがある**
   `instructor` は活発に開発されているライブラリで、メジャーバージョンアップ時に `instructor.patch()` から `instructor.from_openai()` のような形式に変わるなど、APIが変更された経緯があります。導入時は公式リポジトリのCHANGELOGやドキュメントで現在の推奨APIを確認してください。

6. **機微情報を含む入力の扱いに注意**
   請求書や個人情報を含むテキストを外部LLM APIに送信する場合、各プロバイダの利用規約やデータ取り扱いポリシーを確認し、必要に応じてマスキングやオンプレミス/VPC環境のモデル利用を検討してください。

## FAQ

**Q1. instructor を使わずに `response_format={"type": "json_object"}` だけではダメですか？**

A. OpenAIのJSONモードは「有効なJSONを返す」ことは保証しますが、指定したスキーマ通りのキーや型になることまでは保証しません。`instructor` はPydanticモデルによる型・制約のバリデーションと、失敗時の自動リトライまでを一体で提供するため、より堅牢に「欲しい形のデータ」を得られます。シンプルなJSON取得だけで十分な場合はJSONモードでも問題ありませんが、型安全性や複雑なネスト構造、業務ロジックのバリデーションが必要な場合は `instructor` の方が実装コストを削減できます。

**Q2. Anthropic の Claude でも同じように使えますか？**

A. 使えます。`instructor.from_anthropic(Anthropic())` のようにクライアントをラップすれば、OpenAI版とほぼ同じインターフェース（`response_model` を渡す形）で利用できます。ただし内部的にはAnthropicのTool Use機能を利用しているため、モデルごとのツール呼び出し精度の違いには留意してください。

```python
from anthropic import Anthropic
import instructor

client = instructor.from_anthropic(Anthropic())

user = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    response_model=UserInfo,
    messages=[{"role": "user", "content": "田中太郎さんは32歳です。"}],
)
```

**Q3. リトライを重ねても毎回バリデーションに失敗する場合、どう対処すればいいですか？**

A. まず `max_retries` を無制限に近い値にしないことが重要です（コスト・レイテンシの暴発を防ぐため、3〜5回程度が目安）。そのうえで、失敗が続く場合は以下を見直してください。

- Pydanticモデルの `Field(description=...)` が曖昧でないか（LLMが何を抽出すべきか具体的に書く）
- バリデーションルールが厳しすぎないか（本当に必須なフィールドかを再検討する）
- そもそも入力テキストに抽出対象の情報が含まれているか

それでも失敗する場合は、`instructor` の `create_with_completion` を使って生のレスポンスも合わせて取得し、失敗理由をログに残してデバッグする方法が有効です。

```python
user, completion = client.chat.completions.create_with_completion(
    model="gpt-4o-mini",
    response_model=UserInfo,
    messages=[{"role": "user", "content": "..."}],
)
print(completion.usage)  # トークン使用量なども確認できる
```

---

`instructor` は「LLMの出力をとにかく構造化してアプリケーションに組み込みたい」というニーズに対して、Pydanticという既に多くのPython開発者が慣れ親しんだツールをそのまま活用できる点が最大の強みです。まずは小さな抽出タスクから導入し、バリデーションルールを少しずつ厳密化していくのが実務での定着の近道です。
