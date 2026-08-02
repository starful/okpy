---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250324104353.png
date: 2025-03-26
hatena_path: /entry/2025/03/26/060454
slug: python-xlrdライブラリの基本的な使い方
summary: Python の xlrd ライブラリは、Excel ファイル（.xls）の読み取り専用ライブラリです。主に旧形式の Excel（2003 以前）ファイルのデータ取得に使用されます。本記事では、xlrd
  の基本的な使い方と注意点を紹介します。
title: Python xlrdライブラリの基本的な使い方
---

# Python xlrdライブラリの基本的な使い方

# Python `xlrd` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250324104353.png)

Python の `xlrd` ライブラリは、Excel ファイル（.xls）の読み取り専用ライブラリです。主に旧形式の Excel（2003 以前）ファイルのデータ取得に使用されます。本記事では、`xlrd` の基本的な使い方と注意点を紹介します。

## 1. `xlrd` ライブラリの概要

- `.xls`（Excel 97-2003）形式のファイル読み取り専用です。
- `.xlsx` 形式には 2.0.0 以降のバージョンでは非対応。
- 書き込み機能はなく、読み取りのみ可能です。

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install xlrd==1.2.0
```
</div>

📌 `xlsx` を読みたい場合は `openpyxl` を使いましょう。

---

## 2. 主な機能と使用例

### (1) Excel ファイル（.xls）の読み込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import xlrd

book = xlrd.open_workbook("sample.xls")
sheet = book.sheet_by_index(0)
print(sheet.name)
```
</div>

### (2) シート名の取得と選択

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
print(book.sheet_names())
sheet = book.sheet_by_name("Sheet1")
```
</div>

### (3) セルの値を取得する

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
value = sheet.cell_value(rowx=0, colx=0)
print(value)
```
</div>

### (4) 行・列のデータ取得

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
row = sheet.row_values(0)
col = sheet.col_values(1)
print(row)
print(col)
```
</div>

### (5) シートの行数と列数を取得

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
print(sheet.nrows)
print(sheet.ncols)
```
</div>

### (6) すべてのセルをループで取得

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
for row_idx in range(sheet.nrows):
    for col_idx in range(sheet.ncols):
        print(sheet.cell_value(row_idx, col_idx))
```
</div>

### (7) データ型の確認（cell_type）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
ctype = sheet.cell_type(0, 0)
print(ctype)  # 0=empty, 1=text, 2=number, etc.
```
</div>

### (8) 日付データの扱い（xldate_as_tuple）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from datetime import datetime
from xlrd.xldate import xldate_as_tuple

date_value = sheet.cell_value(1, 2)
date_tuple = xldate_as_tuple(date_value, book.datemode)
date = datetime(*date_tuple)
print(date)
```
</div>

### (9) エラー処理：ファイル形式確認

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
try:
    book = xlrd.open_workbook("data.xlsx")
except xlrd.biffh.XLRDError:
    print("xlsx形式には対応していません")
```
</div>

### (10) ファイルが存在しない場合の対処

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import os

filename = "sample.xls"
if os.path.exists(filename):
    book = xlrd.open_workbook(filename)
else:
    print("ファイルが見つかりません")
```
</div>

---

## 3. `xlrd` の主な機能まとめ

| 機能 | 説明 |
|------|------|
| `.xls` ファイル対応 | Excel 2003 形式専用の読み取りライブラリ |
| シートの読み取り | インデックスまたは名前で取得可能 |
| セルの操作 | 値取得、型取得、行・列の一括取得 |
| 日付データ対応 | `xldate_as_tuple` で datetime に変換可能 |

---

## まとめ

`xlrd` は古い Excel ファイル（.xls）のデータを扱う際に非常に便利です。現在では `xlsx` の読み込みには `openpyxl` や `pandas` を使用することが推奨されますが、レガシーデータ対応には `xlrd` の知識も欠かせません！