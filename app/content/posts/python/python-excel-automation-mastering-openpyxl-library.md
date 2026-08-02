---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250324104104.png
date: 2025-03-25
hatena_path: /entry/2025/03/25/104509
slug: python-excel-automation-mastering-openpyxl-library
summary: Python の openpyxl ライブラリは、Excel ファイル（.xlsx）の読み書きを行うための標準的なライブラリです。本記事では、openpyxl
  の基本操作から応用例まで、コピー機能付きコードブロックとともに紹介します。
title: 'Python Excel Automation: Mastering openpyxl Library'
---

# Python Excel Automation: Mastering openpyxl Library

# Python `openpyxl` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250324104104.png)

Python の `openpyxl` ライブラリは、Excel ファイル（.xlsx）の読み書きを行うための標準的なライブラリです。本記事では、`openpyxl` の基本操作から応用例まで、コピー機能付きコードブロックとともに紹介します。

## 1. `openpyxl` ライブラリの概要

- Excel 2010 以降の `.xlsx` 形式に対応。
- 読み込み・書き込み・セルの編集・スタイル設定・グラフ作成などが可能。
- VBA マクロや `.xls` 形式（旧形式）には非対応です。

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install openpyxl
```
</div>

---

## 2. 主な機能と使用例

### (1) Excel ファイルの新規作成

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws['A1'] = 'こんにちは！'
wb.save("sample.xlsx")
```
</div>

### (2) 既存の Excel ファイルを読み込む

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from openpyxl import load_workbook

wb = load_workbook("sample.xlsx")
ws = wb.active
print(ws['A1'].value)
```
</div>

### (3) セルの値を変更する

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
ws['A1'] = '変更されたテキスト'
wb.save("sample.xlsx")
```
</div>

### (4) セルのスタイル設定（フォント・色）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from openpyxl.styles import Font, PatternFill

ws['A1'].font = Font(bold=True, color="FFFFFF")
ws['A1'].fill = PatternFill(start_color="0000FF", end_color="0000FF", fill_type="solid")
wb.save("styled.xlsx")
```
</div>

### (5) 行や列の追加・削除

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
ws.insert_rows(2)  # 2行目に挿入
ws.delete_cols(1)  # 1列目を削除
wb.save("modified.xlsx")
```
</div>

### (6) 複数のシートを操作する

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
ws1 = wb.create_sheet(title="データ")
ws2 = wb.create_sheet(title="レポート")
print(wb.sheetnames)
wb.save("multisheet.xlsx")
```
</div>

### (7) セル範囲のループ処理

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
for row in ws["A1:C3"]:
    for cell in row:
        print(cell.value)
```
</div>

### (8) セルの結合と解除

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
ws.merge_cells("A1:C1")
ws.unmerge_cells("A1:C1")
wb.save("merged.xlsx")
```
</div>

### (9) グラフの作成（棒グラフ）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from openpyxl.chart import BarChart, Reference

values = Reference(ws, min_col=2, min_row=1, max_col=2, max_row=4)
chart = BarChart()
chart.add_data(values, titles_from_data=True)
ws.add_chart(chart, "E5")
wb.save("chart.xlsx")
```
</div>

### (10) 条件付き書式の適用

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import PatternFill

red_fill = PatternFill(start_color="FFCCCC", end_color="FFCCCC", fill_type="solid")
ws.conditional_formatting.add("B2:B10", CellIsRule(operator="greaterThan", formula=["100"], fill=red_fill))
wb.save("conditional.xlsx")
```
</div>

---

## 3. `openpyxl` の主な機能一覧

| 機能 | 説明 |
|------|------|
| `Workbook` / `load_workbook` | 新規作成・既存ファイルの読み込み |
| `Cell` の操作 | 値の読み書き、結合、スタイル適用 |
| `Worksheet` 管理 | 複数シートの追加・削除・移動 |
| `Chart` 機能 | 棒グラフや折れ線グラフなどの作成 |
| `Conditional Formatting` | 条件付き書式の適用 |

---

## まとめ

`openpyxl` を使えば、Excel ファイルの作成から編集、視覚的な装飾やグラフ作成まで、Python で幅広い操作が可能になります。業務自動化やレポート作成など、様々なシーンで活用できる非常に便利なライブラリです！