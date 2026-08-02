---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250305142149.png
date: 2025-03-05
hatena_path: /entry/2025/03/05/142114
slug: 文字列操作の強力なツール-pythonのreライブラリ
summary: Python 標準ライブラリの re は、正規表現（Regular Expressions）を扱うための強力なツールです。文字列の検索、置換、抽出、パターンマッチングなど、テキスト処理を行う際に非常に役立ちます。本記事では、re
  ライブラリの基本概念から実践的な使用例までを詳しく解説します。
title: 文字列操作の強力なツール：Pythonのreライブラリ
---

# 文字列操作の強力なツール：Pythonのreライブラリ

# Python `re` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250305142149.png)

Python 標準ライブラリの `re` は、正規表現（Regular Expressions）を扱うための強力なツールです。文字列の検索、置換、抽出、パターンマッチングなど、テキスト処理を行う際に非常に役立ちます。本記事では、`re` ライブラリの基本概念から実践的な使用例までを詳しく解説します。

## 1. `re` ライブラリの概要

- `re` は、正規表現を使用して文字列を処理するための標準ライブラリです。
- テキストデータの検索、抽出、置換、分割などが可能です。
- Webスクレイピング、ログ解析、データクレンジングなど幅広く活用されます。

### **インストール方法**
`re` は Python の標準ライブラリなので、追加のインストールは不要です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import re
```

---

## 2. 主な機能と使用例

### (1) 文字列の検索（`re.search`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import re

text = "Pythonで正規表現を学ぶ"
pattern = "正規表現"

match = re.search(pattern, text)
if match:
    print("一致する文字列を発見:", match.group())
```

**使用例:**
特定のキーワードを含むログファイルやテキストデータを検索する際に利用できます。

---

### (2) 文字列の一致判定（`re.match`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import re

text = "Python123"
pattern = r"^Python[0-9]+$"

if re.match(pattern, text):
    print("パターンに一致しました！")
else:
    print("一致しませんでした。")
```

**使用例:**
特定のフォーマットに従った入力（例: ユーザー名、パスワード、日付形式など）をチェックする際に使用できます。

---

### (3) すべての一致を取得（`re.findall`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import re

text = "メール: user1@example.com, user2@example.net"
pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

emails = re.findall(pattern, text)
print("見つかったメールアドレス:", emails)
```

**使用例:**
メールアドレス、電話番号、URL などのパターンを抽出する際に利用できます。

---

### (4) 文字列の置換（`re.sub`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import re

text = "Hello 123, this is a test 456."
pattern = r"\d+"

# 数字を * に置換
new_text = re.sub(pattern, "*", text)
print("置換後のテキスト:", new_text)
```

**使用例:**
機密情報（例: 電話番号やクレジットカード番号）をマスキングする際に活用できます。

---

### (5) 文字列の分割（`re.split`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import re

text = "apple, banana; cherry|grape"
pattern = r"[,;|]"

words = re.split(pattern, text)
print("分割結果:", words)
```

**使用例:**
異なる区切り文字を含むテキストデータを分割する際に便利です。

---

## 3. `re` の正規表現パターン

| パターン       | 説明 |
|--------------|------|
| `.`          | 任意の1文字 |
| `^`          | 行の先頭 |
| `$`          | 行の末尾 |
| `\d`         | 数字（0-9） |
| `\w`         | 英数字（a-z, A-Z, 0-9, _） |
| `\s`         | 空白文字 |
| `*`          | 0回以上の繰り返し |
| `+`          | 1回以上の繰り返し |
| `{n,m}`      | n回以上m回以下の繰り返し |

---

## まとめ
Python の `re` ライブラリは、テキスト処理やデータ抽出を効率的に行うための強力なツールです。ログ解析、データクレンジング、Webスクレイピングなどの場面で役立ちます。正規表現の活用をマスターして、より高度なテキスト処理を実現しましょう！ 🚀