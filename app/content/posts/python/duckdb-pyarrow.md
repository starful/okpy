---
title: 'DuckDBとpyarrow連携で爆速データ分析：実践ガイド'
date: 2026-11-20
category: python
slug: duckdb-pyarrow
summary: '- DuckDBはApache Arrow（pyarrow）とゼロコピーに近い形で連携でき、Pandas経由より高速かつ省メモリにデータ分析ができる - `duckdb.sql()`にpyarrow Table/Dataset/RecordBatchReaderを直接渡せるため、CSV→Pandas→DuckDB…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261120170350.jpg'
lang: ja
---

# DuckDBとpyarrow連携で爆速データ分析：実践ガイド

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261120170350.jpg)


## TL;DR

- DuckDBはApache Arrow（pyarrow）とゼロコピーに近い形で連携でき、Pandas経由より高速かつ省メモリにデータ分析ができる
- `duckdb.sql()`にpyarrow Table/Dataset/RecordBatchReaderを直接渡せるため、CSV→Pandas→DuckDBのような無駄な変換が不要になる
- Parquetファイル群に対する大規模集計やフィルタリングは、pyarrow Datasetのパーティションプルーニングと組み合わせると特に効果が大きい

## 概要

DuckDBは「組み込み型のOLAP（分析用）データベース」です。SQLiteのようにサーバーレスで動作しながら、列指向ストレージとベクトル化実行エンジンを備えており、数GB〜数十GB規模のデータ分析をノートPC上でも高速にこなせます。

一方、pyarrowはApache Arrowプロジェクトの公式Python実装で、列指向のメモリフォーマット（Arrow形式）を提供します。DuckDBの内部実行エンジンもArrow形式と親和性が高く、両者を組み合わせることで以下のメリットが得られます。

1. **ゼロコピーに近いデータ受け渡し**：pyarrow TableをDuckDBに渡す際、Pandasのように型変換やコピーのオーバーヘッドが少ない
2. **メモリ効率**：Pandasのオブジェクト型（特に文字列）に比べ、Arrowの列指向フォーマットは省メモリ
3. **Parquet/Datasetとの統合**：pyarrow.datasetの遅延評価・述語プッシュダウンと、DuckDBのクエリオプティマイザが組み合わさり、必要な列・行だけを読み込める
4. **ストリーミング処理**：巨大なデータをメモリに全部載せず、RecordBatchReaderで逐次処理できる

実務では「S3やローカルに溜まった大量のParquetログを集計したい」「Pandasでは重すぎる中間テーブルをSQLで捌きたい」といった場面で威力を発揮します。

## インストール

```bash
pip install duckdb pyarrow pandas
```

バージョンの目安（2026年時点の安定運用ライン）:

```bash
pip install "duckdb>=1.1" "pyarrow>=16.0"
```

Jupyter環境で使う場合は追加で以下もあると便利です。

```bash
pip install duckdb-engine  # SQLAlchemy経由で使いたい場合のみ
```

## 基本サンプル

### 1. pyarrow TableをDuckDBに直接クエリする

```python
import duckdb
import pyarrow as pa

# サンプルのpyarrow Tableを作成
table = pa.table({
    "user_id": [1, 2, 3, 4, 5],
    "country": ["JP", "US", "JP", "KR", "JP"],
    "amount": [1200, 3400, 800, 2100, 950],
})

# pyarrow Tableをそのままテーブルのように扱える
# （ローカル変数名がそのままFROM句のテーブル名になる）
result = duckdb.sql("""
    SELECT country, SUM(amount) AS total_amount, COUNT(*) AS cnt
    FROM table
    GROUP BY country
    ORDER BY total_amount DESC
""")

print(result)  # duckdb.DuckDBPyRelationとして表示される

# 必要に応じてpyarrow Tableに戻す／Pandasに変換する
arrow_result = result.arrow()
df = result.df()
```

ポイントは、`FROM table`のようにPythonスコープ上のpyarrowオブジェクトをSQLから直接参照できることです。CSVを読み込んでPandasに変換し、それをDuckDBに食わせるという二度手間が不要になります。

### 2. Parquetファイル群（pyarrow Dataset）を集計する

実務で最も使うパターンです。日付パーティションで分割されたログを例にします。

```python
import duckdb
import pyarrow.dataset as ds

# S3やローカルディレクトリ配下のParquet群をDatasetとして定義
# （実際にファイルは読み込まず、スキーマとパーティション情報だけを把握する）
dataset = ds.dataset(
    "s3://my-bucket/logs/",
    format="parquet",
    partitioning="hive",  # year=2026/month=11/day=20/ のような構造を想定
)

con = duckdb.connect()

query = """
    SELECT
        year, month,
        event_type,
        COUNT(*) AS event_count
    FROM dataset
    WHERE year = 2026 AND month = 11
    GROUP BY year, month, event_type
    ORDER BY event_count DESC
"""

df = con.execute(query).df()
print(df.head(10))
```

この書き方では、`WHERE year = 2026 AND month = 11`の条件がpyarrow Datasetのパーティションプルーニングに伝わり、該当しないファイルはそもそもスキャン対象から除外されます。さらにDuckDB側で列プルーニング（`event_type`など使う列だけ読み込む）も効くため、ディスクI/Oが大幅に削減されます。

### 3. 大容量データをストリーミングで処理する（RecordBatchReader）

メモリに載せきれないデータを扱う場合は、結果セットをRecordBatchReaderとして受け取り、バッチ単位で処理します。

```python
import duckdb

con = duckdb.connect("analytics.duckdb")

rel = con.sql("""
    SELECT user_id, event_type, created_at
    FROM read_parquet('data/events_*.parquet')
    WHERE created_at >= '2026-10-01'
""")

# バッチ単位（デフォルトは約1024〜2048行程度）でArrow RecordBatchを取得
reader = rel.fetch_arrow_reader(batch_size=100_000)

total_rows = 0
for batch in reader:
    # batch は pyarrow.RecordBatch
    total_rows += batch.num_rows
    # ここでバッチごとの集計・変換処理などを行う
    # 例: 外部システムへの逐次書き込み、独自の変換処理など

print(f"処理した行数: {total_rows}")
```

全件をPandas DataFrameに変換してからループするのと違い、メモリ使用量をバッチサイズ程度に抑えられるのが利点です。

### 4. Pandas混在のワークフロー

既存のPandas資産を活かしつつDuckDBで重い集計だけ肩代わりさせる、という使い方も現実的です。

```python
import duckdb
import pandas as pd

df_orders = pd.read_csv("orders.csv")
df_customers = pd.read_csv("customers.csv")

# 複数のDataFrameをJOINする重い処理をDuckDBに任せる
result_df = duckdb.sql("""
    SELECT
        c.customer_name,
        SUM(o.amount) AS total_spent,
        COUNT(o.order_id) AS order_count
    FROM df_orders o
    JOIN df_customers c ON o.customer_id = c.customer_id
    GROUP BY c.customer_name
    HAVING SUM(o.amount) > 10000
    ORDER BY total_spent DESC
""").df()

print(result_df)
```

Pandasの`merge`+`groupby`より可読性が高く、かつ大規模データではDuckDBの方がメモリ効率・速度の両面で有利なケースが多いです。

## 注意点

### 型変換のコストと落とし穴

- PandasのオブジェクトdtypeカラムはArrow変換時に型推論コストがかかることがあります。特に`None`と空文字列が混在する列は意図しない型になりがちなので、事前に`astype`やスキーマ指定で明示するのが安全です。
- DuckDBの`.df()`はPandas DataFrameへの変換、`.arrow()`はpyarrow Tableへの変換ですが、この変換自体にもコピーコストが発生します。最終的にArrow形式で使うなら、不要な`.df()`呼び出しは避けましょう。

### メモリ管理

- DuckDBはデフォルトで利用可能メモリの一定割合までしか使わない設定になっていますが、巨大なJOINやGROUP BYではスピル（ディスクへの一時書き出し）が発生し、想定外に遅くなることがあります。`PRAGMA memory_limit='8GB'`のように明示的に上限を設定し、挙動を把握しておくことを推奨します。
- pyarrow Datasetを使う場合、`ds.dataset()`自体はファイルを即座に読み込みませんが、スキーマ推論のために全ファイルのメタデータを読みに行くことがあります。パーティション数が極端に多い（数万ファイル）場合はこの初期化自体が遅くなるため、`partitioning`を明示的に指定してスキーマ推論の範囲を絞るのが有効です。

### バージョン互換性

- DuckDBとpyarrowはどちらも開発が活発で、APIが変わることがあります。特に`fetch_arrow_reader`や`to_arrow_table`系のメソッド名・引数はバージョン間で差異が出やすいため、本番導入時はrequirements.txtでバージョンを固定し、CIでアップグレード時の挙動変化を検知できるようにしておくと安全です。
- マルチスレッド環境（Webアプリのワーカープロセスなど）で単一の`duckdb.connect()`オブジェクトを使い回す場合、スレッドセーフ性の制約があるため、スレッド/プロセスごとにコネクションを分けるのが無難です。

### SQLインジェクション的な注意

- ユーザー入力をそのままSQL文字列に埋め込むと、通常のSQLデータベースと同様にインジェクションのリスクがあります。`con.execute(query, params)`のようにパラメータバインディングを使い、動的な値は文字列結合しないようにしましょう。

## FAQ

**Q1. DuckDBとpyarrowを両方インストールする必要がありますか？DuckDB単体でParquetは読めますよね？**

A. その通りで、`read_parquet()`関数を使えばpyarrowなしでもDuckDB単体でParquet読み込みは可能です。ただし、既存のPandas/pyarrowベースのパイプライン（pyarrow Dataset、既存のpyarrow Table、他ライブラリが返すArrowオブジェクトなど）と組み合わせたい場合や、ストリーミング処理でRecordBatchReaderを扱いたい場合はpyarrowが必要になります。「既存資産との連携」が主目的であれば両方入れておくのが無難です。

**Q2. Pandasに変換せず、常にpyarrow形式のまま処理した方が速いですか？**

A. 一般的にはYesですが、常にそうとは限りません。Pandas特有の操作（特定のライブラリとの連携、matplotlibでの可視化など）が必要な場合は、最終段階でだけPandasに変換するのが現実的です。重要なのは「中間処理の段階で不要な変換を挟まない」ことです。DuckDB → Arrow → 必要な処理 → 最終的にPandasへ、という順序を意識すれば、中間のメモリコピーを最小限にできます。

**Q3. S3上の大量のParquetファイルを分析したいのですが、ローカルにダウンロードせずに直接クエリできますか？**

A. 可能です。DuckDBには`httpfs`拡張機能があり、`INSTALL httpfs; LOAD httpfs;`を実行した上で`read_parquet('s3://bucket/path/*.parquet')`のようにS3パスを直接指定できます。認証情報は環境変数（`AWS_ACCESS_KEY_ID`など）やDuckDBの`SECRET`機能で設定します。pyarrow側の`ds.dataset()`でも`filesystem`引数にs3fsなどを渡すことでS3上のデータセットを扱えます。大規模データの場合は、まずパーティション条件（日付など）で絞り込んでからクエリすることで、転送量とコストを抑えられます。

---

DuckDBとpyarrowの組み合わせは、「Pandasだと重い」「かといってSparkのような分散基盤を立てるほどでもない」という中間的な規模のデータ分析に最適な選択肢です。既存のArrowエコシステム（pyarrow、Polars、Parquetなど）と親和性が高いため、段階的に既存コードへ導入しやすい点も実務上のメリットと言えます。
