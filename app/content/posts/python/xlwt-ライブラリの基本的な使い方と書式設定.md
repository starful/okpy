---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250324104601.png
date: 2025-03-28
hatena_path: /entry/2025/03/28/090040
slug: xlwt-ライブラリの基本的な使い方と書式設定
summary: Python の xlwt ライブラリは、Excel 2003 形式（.xls）のファイルを書き込むための専用ライブラリです。openpyxl が
  .xlsx に対応しているのに対し、xlwt は .xls を対象としています。本記事では xlwt の基本的な使い方と書式設定の方法などを紹介します。
title: xlwt ライブラリの基本的な使い方と書式設定
---

# xlwt ライブラリの基本的な使い方と書式設定

# Python `xlwt` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250324104601.png)

Python の `xlwt` ライブラリは、Excel 2003 形式（.xls）のファイルを書き込むための専用ライブラリです。`openpyxl` が `.xlsx` に対応しているのに対し、`xlwt` は `.xls` を対象としています。本記事では `xlwt` の基本的な使い方と書式設定の方法などを紹介します。

## 1. `xlwt` ライブラリの概要

- `.xls`（Excel 97-2003）形式のファイル出力に特化。
- セルへの文字列、数値、日付、スタイルの書き込みが可能。
- 読み込みは非対応（読み込みには `xlrd` を使用）。
- `.xlsx`（Excel 2007 以降）形式には対応していません。

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install xlwt
```
</div>

---

## 2. 主な機能と使用例

### (1) 新しい Excel ファイルの作成と保存

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import xlwt

wb = xlwt.Workbook()
ws = wb.add_sheet("Sheet1")
ws.write(0, 0, "こんにちは")
wb.save("output.xls")
```
</div>

### (2) 数値や日付の書き込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import datetime

ws.write(1, 0, 123.45)
ws.write(2, 0, datetime.datetime.now().strftime("%Y-%m-%d"))
```
</div>

### (3) フォントのスタイル変更（太字・色）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
style = xlwt.easyxf('font: bold 1, color red;')
ws.write(3, 0, "太字の赤文字", style)
```
</div>

### (4) 列幅の調整

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
ws.col(0).width = 256 * 20  # 20文字分の幅に設定
```
</div>

### (5) 行の高さの調整

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
ws.row(0).height_mismatch = True
ws.row(0).height = 20 * 20  # 高さを設定（20pt）
```
</div>

### (6) セルの罫線設定

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
borders = xlwt.Borders()
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN

style = xlwt.XFStyle()
style.borders = borders
ws.write(4, 0, "罫線付きセル", style)
```
</div>

### (7) 複数シートの作成

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
sheet2 = wb.add_sheet("分析")
sheet2.write(0, 0, "分析用データ")
```
</div>

### (8) 書式を複数適用（結合スタイル）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
style = xlwt.easyxf('font: bold 1; pattern: pattern solid, fore_color yellow;')
ws.write(5, 0, "強調表示", style)
```
</div>

### (9) 数値書式（通貨・小数点）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
style = xlwt.XFStyle()
style.num_format_str = '#,##0.00'
ws.write(6, 0, 1234567.89, style)
```
</div>

### (10) 保存してファイルを閉じる

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
wb.save("styled_output.xls")
```
</div>

---

## 3. `xlwt` の主な機能まとめ

| 機能 | 説明 |
|------|------|
| `.xls` 出力対応 | Excel 2003 形式の書き込み専用ライブラリ |
| セル書き込み | 文字列、数値、日付、スタイルの書き込み |
| 書式設定 | フォント、罫線、背景色、数値フォーマットなど |
| 複数シート | 複数のシートを1つのブックに追加可能 |

---

## まとめ

`xlwt` はレガシー Excel ファイルへの書き込みに最適なライブラリです。現在では `.xlsx` 形式の利用が主流ですが、旧システムとの連携やレガシーファイルの自動出力には `xlwt` の知識が役立ちます！