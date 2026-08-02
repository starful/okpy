---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250306095649.png
date: 2025-03-06
hatena_path: /entry/2025/03/06/095718
slug: python-jsonライブラリの基本
summary: Python 標準ライブラリの json は、JSON（JavaScript Object Notation）データを扱うための便利なツールです。本記事では、json
  ライブラリの基本概念から実践的な使用例までを詳しく解説します。
title: PythonでJSONを扱う基本：jsonモジュールの使い方（読み込み・書き込み・変換）
description: Python標準のjsonモジュールを使って、JSONデータの変換（エンコード・デコード）、読み込み（load/loads）、書き込み（dump/dumps）を行う基本手順を初心者向けに解説します。
seo_title: Python JSON変換・読み込み・書き込み徹底解説（loads/dumpsの使い方） | OKPy
seo_description: Pythonの標準jsonライブラリを使ったJSONデータの読み込み（load/loads）、書き込み（dump/dumps）、日本語エンコードなどの変換方法をコード付きでわかりやすく解説します。
---


# Python JSONライブラリの基本

# Python `json` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250306095649.png)

Python 標準ライブラリの `json` は、JSON（JavaScript Object Notation）データを扱うための便利なツールです。本記事では、`json` ライブラリの基本概念から実践的な使用例までを詳しく解説します。

## 1. `json` ライブラリの概要

- `json` は Python のデータを JSON 形式に変換したり、JSON を Python データに変換するための標準ライブラリです。
- Web API のデータ送受信や、設定ファイルの読み書きに広く活用されます。
- JSON 形式は、軽量で可読性が高いため、さまざまなプログラミング言語で使用されます。

### **インストール方法**
`json` は Python の標準ライブラリなので、追加のインストールは不要です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json
```

---

## 2. 主な機能と使用例

### (1) Python オブジェクトを JSON 文字列に変換（`json.dumps`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json

# Python の辞書を JSON 文字列に変換
data = {"name": "Alice", "age": 25, "city": "Tokyo"}
json_string = json.dumps(data)
print("JSON 文字列:", json_string)
```

**使用例:**
データを JSON 形式に変換し、Web API へ送信する際に利用できます。

---

### (2) JSON 文字列を Python オブジェクトに変換（`json.loads`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json

# JSON 文字列を Python の辞書に変換
json_string = '{"name": "Alice", "age": 25, "city": "Tokyo"}'
data = json.loads(json_string)
print("Python オブジェクト:", data)
```

**使用例:**
Web API から受け取った JSON データを Python の辞書として処理できます。

---

### (3) JSON データをファイルに保存（`json.dump`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json

# Python データを JSON ファイルに保存
data = {"name": "Alice", "age": 25, "city": "Tokyo"}
with open("data.json", "w") as f:
    json.dump(data, f, indent=4)
```

**使用例:**
設定データやログデータを JSON ファイルに保存する際に活用できます。

---

### (4) JSON ファイルを読み込む（`json.load`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json

# JSON ファイルを Python データに読み込む
with open("data.json", "r") as f:
    data = json.load(f)
print("読み込んだデータ:", data)
```

**使用例:**
設定ファイルを JSON 形式で保存し、プログラム起動時に読み込む場合に使用できます。

---

### (5) JSON のフォーマットを見やすくする

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json

# 整形された JSON 文字列を生成
data = {"name": "Alice", "age": 25, "city": "Tokyo"}
pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
print(pretty_json)
```

**使用例:**
JSON データをデバッグする際に可読性を向上させるために活用されます。

---

### (6) JSON データのキーのソート

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json

# JSON のキーをソートして出力
data = {"city": "Tokyo", "name": "Alice", "age": 25}
sorted_json = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
print(sorted_json)
```

**使用例:**
JSON データのキーを統一された順序で整理する際に使用できます。

---

### (7) ネストされた JSON の処理

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json

# ネストされた JSON を処理
data = {
    "user": {
        "name": "Alice",
        "details": {
            "age": 25,
            "city": "Tokyo"
        }
    }
}

# ネストされた値の取得
print("名前:", data["user"]["name"])
print("年齢:", data["user"]["details"]["age"])
```

**使用例:**
多階層の JSON データを処理する際に活用できます。

---

### (8) JSON データのマージ（複数の JSON を統合）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json

# 2つの JSON オブジェクトをマージ
data1 = {"name": "Alice", "age": 25}
data2 = {"city": "Tokyo", "country": "Japan"}

merged_data = {**data1, **data2}
print(json.dumps(merged_data, indent=4, ensure_ascii=False))
```

**使用例:**
異なる JSON データを統合し、一つの JSON ファイルにまとめる際に利用できます。

---

### (9) JSON データの特定キー削除

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json

# JSON データ内の特定キーを削除
data = {"name": "Alice", "age": 25, "city": "Tokyo"}
del data["age"]

print(json.dumps(data, indent=4, ensure_ascii=False))
```

**使用例:**
不要なデータを削除し、必要な情報だけを保存したい場合に活用できます。

---

### (10) JSON データの検証（正しい JSON かチェック）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import json

def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False

# テスト
json_str = '{"name": "Alice", "age": 25}'
print("JSON が有効か:", is_valid_json(json_str))
```

**使用例:**
外部から受け取った JSON データが正しい形式かチェックする際に活用できます。

---

## 3. `json` のオプション設定

| オプション        | 説明 |
|------------------|------|
| `indent=4`      | インデントを設定し、見やすくフォーマットする |
| `ensure_ascii=False` | 日本語などの非ASCII文字をそのまま表示する |
| `sort_keys=True` | キーをアルファベット順に並べる |

---

## まとめ
Python の `json` ライブラリは、JSON データの処理を簡単に行うための強力なツールです。API 連携、設定ファイルの保存、データ交換など幅広い用途に利用できます。`json` を活用して、より便利なデータ管理を実現しましょう！ 🚀