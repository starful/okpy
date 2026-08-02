---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250324122026.png
date: 2025-03-30
hatena_path: /entry/2025/03/30/070329
slug: 高速なデータ処理を可能にするpythonのpolarsライブラリガイド
summary: Python の polars ライブラリは、高速かつメモリ効率の良いデータフレーム操作を可能にする次世代のデータ分析ツールです。特に大規模データの処理において優れたパフォーマンスを発揮します。本記事では
  polars の主要機能と使い方を、コピー機能付きコードブロックで紹介します。
title: 高速なデータ処理を可能にするPythonのpolarsライブラリガイド
---

# 高速なデータ処理を可能にするPythonのpolarsライブラリガイド

# Python `polars` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250324122026.png)

Python の `polars` ライブラリは、高速かつメモリ効率の良いデータフレーム操作を可能にする次世代のデータ分析ツールです。特に大規模データの処理において優れたパフォーマンスを発揮します。本記事では `polars` の主要機能と使い方を、コピー機能付きコードブロックで紹介します。

## 1. `polars` ライブラリの概要

- Rust ベースで構築されており、非常に高速。
- `pandas` ライクな API を提供しつつ、非同期処理やマルチスレッドを活用。
- lazy モードと eager モードの両方をサポート。

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install polars
```
</div>

---

## 2. 主な機能と使用例

### (1) DataFrame の作成

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import polars as pl

df = pl.DataFrame({"名前": ["Alice", "Bob"], "年齢": [25, 30]})
print(df)
```
</div>

### (2) CSV ファイルの読み込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
df = pl.read_csv("data.csv")
print(df.head())
```
</div>

### (3) フィルタリング（条件抽出）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
filtered = df.filter(pl.col("年齢") > 25)
print(filtered)
```
</div>

### (4) 集計（groupby）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
df = pl.DataFrame({"カテゴリ": ["A", "B", "A"], "売上": [100, 200, 150]})
gb = df.groupby("カテゴリ").agg(pl.col("売上").sum())
print(gb)
```
</div>

### (5) ソート

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
sorted_df = df.sort("売上", descending=True)
print(sorted_df)
```
</div>

### (6) 列の追加・変更

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
df = df.with_columns([
    (pl.col("売上") * 1.1).alias("税込売上")
])
print(df)
```
</div>

### (7) null 値の処理

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
df = df.fill_null("不明")
print(df)
```
</div>

### (8) LazyFrame（遅延評価）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
df_lazy = df.lazy().filter(pl.col("売上") > 100).collect()
print(df_lazy)
```
</div>

### (9) データの結合（join）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
df1 = pl.DataFrame({"ID": [1, 2], "名前": ["Alice", "Bob"]})
df2 = pl.DataFrame({"ID": [1, 2], "年齢": [25, 30]})
df_joined = df1.join(df2, on="ID")
print(df_joined)
```
</div>

### (10) 書き出し（CSV 保存）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
df.write_csv("output.csv")
```
</div>

---

## 3. `polars` の主な機能まとめ

| 機能 | 説明 |
|------|------|
| `DataFrame` / `LazyFrame` | 高速かつ柔軟なデータ構造（遅延評価対応） |
| `read_csv`, `write_csv` | 高速な読み込み・書き出し |
| `groupby`, `agg` | 高性能な集計処理 |
| `with_columns` | 複数列の一括追加・変換 |
| `join` | 異なる DataFrame の結合 |

---

## まとめ

`polars` は、`pandas` に代わる次世代のデータ処理ライブラリとして注目されています。大規模データや高速処理が求められる場面で強力な武器になるため、パフォーマンス重視の分析にはぜひ活用してみましょう！