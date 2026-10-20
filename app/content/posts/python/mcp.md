---
title: 'PythonライブラリmcpによるMCPサーバー・クライアント実践ガイド'
date: 2026-10-20
category: python
slug: mcp
summary: '- `mcp`はAnthropicが提供するModel Context Protocol（MCP）の公式Python SDKで、LLMアプリケーションとツール・データソースを安全に接続するための標準プロトコルを実装できます。 - `FastMCP`を使うとデコレータベースで数行のコードからMCPサーバーを構築でき…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261020151116.jpg'
lang: ja
---

# PythonライブラリmcpによるMCPサーバー・クライアント実践ガイド

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261020151116.jpg)


## TL;DR

- `mcp`はAnthropicが提供するModel Context Protocol（MCP）の公式Python SDKで、LLMアプリケーションとツール・データソースを安全に接続するための標準プロトコルを実装できます。
- `FastMCP`を使うとデコレータベースで数行のコードからMCPサーバーを構築でき、ツール・リソース・プロンプトの公開が容易です。
- 標準入出力（stdio）だけでなくSSE/HTTPトランスポートにも対応しており、ローカルCLI連携からリモートサービス公開まで幅広い用途に使えます。

## 概要

MCP（Model Context Protocol）は、LLM（大規模言語モデル）アプリケーションが外部のツールやデータソースと統一的なプロトコルで通信するためのオープンな規格です。従来、LLMにファイルアクセスやAPI呼び出しの機能を持たせるには、各ベンダー・各フレームワーク独自の方式でツール定義を行う必要がありました。MCPはこれを「サーバー」と「クライアント」という形で分離し、1つのMCPサーバーを実装すれば、Claude Desktop、Claude Code、その他MCP対応クライアントから同じツール群を再利用できるようにします。

`mcp`はこのプロトコルの公式Python実装で、以下の主要な要素を提供します。

- **サーバー（Server）**: ツール（Tools）、リソース（Resources）、プロンプト（Prompts）を公開する側。
- **クライアント（Client）**: サーバーに接続し、公開された機能を呼び出す側。
- **トランスポート（Transport）**: stdio、Streamable HTTP、SSEなど通信方式。

特に`FastMCP`という高レベルAPIが用意されており、Flaskライクなデコレータでツールを定義できるため、学習コストが非常に低いのが特徴です。社内ドキュメント検索、DB参照、社内APIラッパーなど、「LLMに安全に実務データへアクセスさせたい」というニーズに対して、MCPは現実的な選択肢になっています。

## インストール

Python 3.10以上が推奨されます。`uv`または`pip`でインストールできます。

```bash
# uvを使う場合（推奨）
uv add mcp

# pipを使う場合
pip install mcp

# CLI機能やanthropicクライアント連携を含める場合
pip install "mcp[cli]"
```

開発中にサーバーをブラウザから検証したい場合は、公式の`mcp dev`コマンド（MCP Inspector）が便利です。

```bash
mcp dev server.py
```

## 基本サンプル

### 1. 最小構成のMCPサーバー

まずは、四則演算を行うシンプルなツールサーバーを作成します。

```python
# server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calculator-server")


@mcp.tool()
def add(a: float, b: float) -> float:
    """2つの数値を加算します。"""
    return a + b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """2つの数値を除算します。0での除算はエラーを返します。"""
    if b == 0:
        raise ValueError("ゼロで除算することはできません")
    return a / b


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

このサーバーは`stdio`で起動し、Claude DesktopやClaude Codeの設定ファイルにパスを登録するだけで利用できます。

### 2. リソースを公開する

ツールだけでなく、読み取り専用のデータを「リソース」として公開することもできます。実務では社内ドキュメントや設定ファイルの参照用途に向いています。

```python
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("docs-server")

DOCS_DIR = Path("./docs")


@mcp.resource("docs://{filename}")
def read_doc(filename: str) -> str:
    """指定したドキュメントファイルの内容を返します。"""
    target = (DOCS_DIR / filename).resolve()

    # パストラバーサル対策: DOCS_DIR配下以外へのアクセスを禁止
    if not target.is_relative_to(DOCS_DIR.resolve()):
        raise ValueError("許可されていないパスです")

    if not target.exists():
        raise FileNotFoundError(f"{filename} が見つかりません")

    return target.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

ここでは`is_relative_to`でパストラバーサルを防いでいる点が実務上重要です。MCPサーバーはローカルファイルへのアクセスを提供することが多いため、入力されたパスの検証を怠るとディレクトリ外のファイルを読み取られる脆弱性になります。

### 3. 実務向け：社内APIをラップするツール

社内REST APIを呼び出すツールの例です。タイムアウトやエラーハンドリングを含め、実運用を意識した書き方にしています。

```python
import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("internal-api-server")

API_BASE_URL = os.environ["INTERNAL_API_BASE_URL"]
API_TOKEN = os.environ["INTERNAL_API_TOKEN"]


@mcp.tool()
async def get_customer_summary(customer_id: str) -> dict:
    """顧客IDを指定して、社内CRMから顧客の概要情報を取得します。"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{API_BASE_URL}/customers/{customer_id}/summary",
                headers=headers,
            )
            response.raise_for_status()
        except httpx.TimeoutException:
            raise RuntimeError("社内APIへの接続がタイムアウトしました")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"社内APIがエラーを返しました: status={e.response.status_code}"
            )

    return response.json()


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

ポイントは以下の3点です。

- APIトークンなどの機密情報は環境変数から読み込み、コードにハードコードしない。
- `httpx.AsyncClient`を使い非同期化することで、複数ツール呼び出しが並行しても詰まらないようにする。
- 例外を握りつぶさず、LLMが理解できる形のエラーメッセージに変換して`RuntimeError`として再送出する（ツール内で例外を出すと、クライアント側にエラー内容が伝わりLLMがリトライや別手段を検討できる）。

### 4. クライアント側からサーバーを呼び出す

自作のPythonアプリからMCPサーバーに接続し、ツールを呼び出す例です。

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 利用可能なツール一覧を取得
            tools = await session.list_tools()
            print([t.name for t in tools.tools])

            # ツールを呼び出す
            result = await session.call_tool("add", arguments={"a": 3, "b": 5})
            print(result.content)


if __name__ == "__main__":
    asyncio.run(main())
```

### 5. Claude Desktop / Claude Codeへの登録

作成したサーバーをClaude Desktopで使う場合、設定ファイル（`claude_desktop_config.json`）に以下のように登録します。

```json
{
  "mcpServers": {
    "calculator-server": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

Claude Codeの場合は`claude mcp add`コマンドでも登録できます。

```bash
claude mcp add calculator-server -- python /absolute/path/to/server.py
```

## 注意点

実務でMCPサーバーを運用する際に特に気をつけるべき点を整理します。

1. **ツールの権限は最小限にする**
   ファイルシステムやDBへのフルアクセスをそのまま公開すると、LLMの誤った判断（プロンプトインジェクション含む）によって意図しない操作が実行されるリスクがあります。読み取り専用で十分な場合は書き込み系ツールを実装しない、削除系ツールには確認フラグを必須にするなど、権限を絞り込むべきです。

2. **入力バリデーションを省略しない**
   LLMが生成する引数は必ずしも安全ではありません。ファイルパス、SQLクエリの断片、シェルコマンドなどを直接組み立てる実装は、インジェクション攻撃の起点になります。上記の`is_relative_to`の例のように、境界チェックを明示的に行ってください。

3. **ツールの説明（docstring）はLLMへの指示として機能する**
   `@mcp.tool()`のdocstringは、LLMがそのツールをいつ・どう使うかを判断する唯一の情報源です。曖昧な説明は誤った呼び出しを招くため、引数の意味・単位・制約（例: 「日付はYYYY-MM-DD形式」）を明記しましょう。

4. **長時間実行・大量データ返却に注意**
   ツールの戻り値はLLMのコンテキストに取り込まれるため、巨大なJSONやログをそのまま返すとコンテキストを圧迫し、応答品質が落ちます。ページネーションや要約を実装側で行うのが望ましいです。

5. **非同期処理とタイムアウトの設計**
   外部API呼び出しを含むツールは必ずタイムアウトを設定してください。設定を忘れると、クライアント側全体がハングし、ユーザー体験を損ないます。

6. **バージョン互換性**
   MCPプロトコル自体もSDKもまだ活発に更新されています。`mcp`パッケージのメジャーバージョンアップでAPI（特に`FastMCP`の初期化引数やトランスポート指定方法）が変わることがあるため、`requirements.txt`や`pyproject.toml`でバージョンを固定し、アップグレード時はCHANGELOGを確認する運用が安全です。

## FAQ

**Q1. MCPサーバーはローカル実行しかできないのですか？**

いいえ。`stdio`トランスポートはローカルプロセス間通信向けですが、`mcp.run(transport="streamable-http")`のようにHTTPベースのトランスポートを指定すれば、リモートホスト上でサーバーを稼働させ、ネットワーク経由でクライアントから接続することも可能です。社内で共有利用するツールサーバーを構築する場合は、こちらを検討してください。ただし認証・アクセス制御を自前で実装する必要がある点には注意が必要です。

**Q2. 既存のREST APIをそのままMCPツールとして公開してよいですか？**

技術的には可能ですが、推奨はしません。REST APIのエンドポイントをそのまま1対1でツール化すると、LLMにとって「どの組み合わせで呼べば目的が達成できるか」が分かりにくくなります。実務では、LLMが達成したいタスク単位（例:「顧客の概要を取得する」）でツールをまとめ、内部で複数のAPI呼び出しを合成する設計のほうが、LLMの呼び出し精度が上がります。

**Q3. エラーハンドリングで気をつけるべきことは何ですか？**

ツール内で発生した例外は、スタックトレースそのままではなく、LLMが次の行動を判断できる自然文のメッセージに変換して伝えるべきです。また、機密情報（内部URL、認証トークン、DB接続文字列など）がエラーメッセージに混入しないように注意してください。上記のコード例のように、`try/except`で捕捉した例外を独自のメッセージに包み直してから再送出するのが安全なパターンです。
