---
title: 'pandas vs polars 徹底比較 – 大規模データ処理はどちらが速いか'
date: 2026-11-20
category: python
slug: pandas-vs-polars
summary: '- polars は Rust 製で並列処理・遅延評価に最適化されており、数百万行規模のデータ処理では pandas より数倍〜数十倍高速になるケースが多い。 - pandas はエコシステム（scikit-learn、matplotlib、既存コードベース）との親和性が高く、中小規模データや既存プロジェクトの保…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261120170239.jpg'
lang: ja
---

# pandas vs polars 徹底比較 – 大規模データ処理はどちらが速いか

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261120170239.jpg)


## TL;DR

- polars は Rust 製で並列処理・遅延評価に最適化されており、数百万行規模のデータ処理では pandas より数倍〜数十倍高速になるケースが多い。
- pandas はエコシステム（scikit-learn、matplotlib、既存コードベース）との親和性が高く、中小規模データや既存プロジェクトの保守では依然として実用的な選択肢。
- 新規プロジェクトでメモリ効率や処理速度が重要な場合は polars を、既存資産や可視化・機械学習ライブラリとの連携を優先する場合は pandas を選ぶのが現実的な指針。

## 概要

データ分析や機械学習の前処理において、Python のデータフレームライブラリは長らく pandas が事実上の標準でした。しかし近年、Rust で実装された polars が登場し、特に大規模データ処理における速度とメモリ効率の面で注目を集めています。

pandas は 2008 年に誕生した歴史あるライブラリで、NumPy をベースにしたシングルスレッド処理が基本です。対して polars は Apache Arrow 形式のメモリレイアウトを採用し、マルチコアでの並列実行や遅延評価（Lazy Evaluation）によるクエリ最適化を標準でサポートしています。

本記事では、両者の API の違い、インストール方法、実務で使えるコード例を比較しながら、どのような場面でどちらを選ぶべきかを解説します。

## インストール

どちらも pip または conda から簡単にインストールできます。

```bash
# pandas のインストール
pip install pandas

# polars のインストール
pip install polars

# 大規模ファイル処理やApache Arrow連携を使う場合は追加パッケージも推奨
pip install pyarrow
```

バージョン確認は以下のコードで行えます。

```python
import pandas as pd
import polars as pl

print("pandas:", pd.__version__)
print("polars:", pl.__version__)
```

## 基本サンプル

### CSV 読み込みと基本統計

まずは同じ CSV ファイルを両方のライブラリで読み込み、基本的な集計処理を比較してみます。

```python
import pandas as pd
import polars as pl
import time

csv_path = "sales_data.csv"  # 例: 1000万行規模の売上データ

# --- pandas ---
start = time.time()
df_pd = pd.read_csv(csv_path)
result_pd = (
    df_pd.groupby("category")["amount"]
    .agg(["sum", "mean", "count"])
    .sort_values("sum", ascending=False)
)
print("pandas 実行時間:", time.time() - start)

# --- polars ---
start = time.time()
df_pl = pl.read_csv(csv_path)
result_pl = (
    df_pl.group_by("category")
    .agg([
        pl.col("amount").sum().alias("sum"),
        pl.col("amount").mean().alias("mean"),
        pl.col("amount").count().alias("count"),
    ])
    .sort("sum", descending=True)
)
print("polars 実行時間:", time.time() - start)
```

このような単純な集計処理でも、データ規模が大きくなるほど polars の並列処理の恩恵が顕著に現れます。手元の検証（100万行〜1000万行規模、8コア環境）では、groupby 集計において polars が pandas の 3〜8 倍程度高速になるケースが多く見られました。

### 遅延評価（Lazy Evaluation）を使った最適化

polars の大きな特徴の一つが、クエリプランを最適化してから実行する遅延評価です。

```python
# polars の Lazy API を使った例
lazy_df = pl.scan_csv("sales_data.csv")

query = (
    lazy_df
    .filter(pl.col("amount") > 1000)
    .group_by("category")
    .agg(pl.col("amount").sum().alias("total_amount"))
    .sort("total_amount", descending=True)
)

# collect() を呼ぶまで実際の計算は実行されない
result = query.collect()
print(result)
```

`scan_csv` を使うとファイル全体を一度にメモリに読み込まず、クエリ最適化（述語プッシュダウンやカラムの刈り込みなど）を行った上で必要な部分だけを処理します。これにより、メモリに乗り切らないような大規模データでも効率的に処理できる場合があります。

### pandas と polars の相互変換

既存の pandas コードを少しずつ polars に移行したい場合、相互変換が可能です。

```python
# pandas DataFrame -> polars DataFrame
df_pl_from_pd = pl.from_pandas(df_pd)

# polars DataFrame -> pandas DataFrame
df_pd_from_pl = df_pl.to_pandas()
```

ただし変換時にはデータ型のマッピング（特に日時型やカテゴリ型）でコストが発生するため、頻繁な相互変換は避け、パイプラインのどこかで片方に統一するのが望ましい設計です。

### 実務でよく使う結合処理の比較

```python
# pandas での結合
merged_pd = df_pd.merge(other_df_pd, on="customer_id", how="left")

# polars での結合
merged_pl = df_pl.join(other_df_pl, on="customer_id", how="left")
```

結合（join）処理においても、polars はハッシュ結合をマルチスレッドで実行するため、大規模テーブル同士の結合では顕著な速度差が出やすい処理の一つです。

## 注意点

実務で両ライブラリを使い分ける際には、以下の点に注意が必要です。

1. **API の違いによる学習コスト**
   polars は pandas と似ているようで、インデックス（index）という概念が存在しない、メソッドチェーンを前提とした設計である、カラム選択に `pl.col()` を使うなど、細部で設計思想が異なります。既存の pandas コードをそのまま置き換えることはできないため、移行には一定の書き換えコストがかかります。

2. **エコシステムの成熟度の差**
   scikit-learn、statsmodels、seaborn など多くのライブラリは pandas DataFrame を前提に設計されています。polars DataFrame を直接渡せないケースも多く、`to_pandas()` での変換が必要になる場面が頻出します。機械学習パイプラインの最終段階では pandas への変換が必要になることを見込んでおくべきです。

3. **小規模データでは差が出にくい、またはオーバーヘッドが勝ることも**
   数千〜数万行程度の小規模データでは、polars の並列化・最適化のオーバーヘッドが相対的に大きくなり、pandas と同等かむしろ pandas の方が速いケースもあります。速度差を実感しやすいのは概ね数十万行以上のデータです。

4. **メモリ使用量は必ずしも「polars が常に有利」ではない**
   Lazy API（`scan_csv` + `collect`）を使わず Eager API（`read_csv` をそのまま使う）で大規模データを扱うと、polars でもメモリに全データを展開するため、pandas と同様にメモリ不足に陥る可能性があります。大規模データでは Lazy API の活用が前提になります。

5. **日本語（マルチバイト文字）やエンコーディングの扱い**
   CSV の文字コードが Shift-JIS や CP932 の場合、pandas では `encoding="cp932"` のように明示的に指定できますが、polars は現状 UTF-8 系のエンコーディングを前提とした実装になっており、非 UTF-8 の日本語 CSV を扱う際には事前に `nkf` や `chardet` 等で UTF-8 に変換する前処理が必要になることがあります。

6. **破壊的変更（Breaking Changes）の頻度**
   polars は活発に開発が進んでいるライブラリであり、バージョンアップに伴い API が変更されることが pandas よりも頻繁にあります。本番パイプラインで使う場合は、`requirements.txt` などでバージョンを固定し、アップデート時には回帰テストを必ず実施してください。

## FAQ

**Q1. 既存の pandas コードを全面的に polars に書き換えるべきですか？**

A. 必ずしもその必要はありません。既存コードが安定稼働しており、かつ処理速度やメモリが問題になっていないのであれば、書き換えによるリスク（バグ混入、学習コスト、保守性低下）の方が大きい場合があります。新規に大規模データパイプラインを構築する場合や、既存処理のボトルネックが明確に groupby・join・フィルタリングにある場合に限定して polars への移行を検討するのが現実的です。

**Q2. polars は pandas より常に速いのですか？**

A. いいえ。前述の通り、数千行〜数万行程度の小規模データでは差がほとんどない、あるいは pandas の方が速いことすらあります。polars の強みは「マルチコア並列処理」と「クエリ最適化（Lazy API）」が効く大規模データ・複雑な集計処理において顕著に現れます。自分のユースケースで実際にベンチマークを取ることを強く推奨します。

**Q3. pandas と polars を同じプロジェクト内で混在させても問題ないですか？**

A. 技術的には `to_pandas()` / `from_pandas()` で相互変換できるため可能ですが、頻繁な変換はオーバーヘッドとコードの複雑化を招きます。実務では「前処理・集計は polars で高速に行い、可視化や機械学習ライブラリに渡す直前に pandas に変換する」というように、パイプラインの役割ごとに明確に使い分けるのが保守性の観点からも推奨されるパターンです。

---

結論として、pandas と polars はどちらが「上位互換」というわけではなく、用途に応じた使い分けが現実的な解です。既存資産とエコシステムの豊富さを重視するなら pandas、大規模データの処理速度とメモリ効率を重視し、新規にパイプラインを構築するなら polars が有力な選択肢となります。実際の導入判断は、必ず自分たちのデータ規模と処理内容でベンチマークを取った上で行うことをお勧めします。
