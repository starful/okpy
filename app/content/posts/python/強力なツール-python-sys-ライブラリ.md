---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250224195504.png
date: 2025-02-24
hatena_path: /entry/2025/02/24/195826
slug: 強力なツール-python-sys-ライブラリ
summary: Python 標準ライブラリの sys は、Python インタープリタと対話するための強力なツールです。本記事では、sys ライブラリの基本概念から実践的な使用例までを詳しく解説します。
title: 強力なツール：Python sys ライブラリ
---

# 強力なツール：Python sys ライブラリ

# Python `sys` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250224195504.png)

Python 標準ライブラリの `sys` は、Python インタープリタと対話するための強力なツールです。本記事では、`sys` ライブラリの基本概念から実践的な使用例までを詳しく解説します。

## 1. `sys` ライブラリの概要

- `sys` は Python インタープリタの動作を制御する標準ライブラリです。
- コマンドライン引数、標準入出力、例外情報、Python のバージョン情報などを取得できます。
- Python 実行環境に関する情報をプログラム内で利用する際に便利です。

### **インストール方法**
`sys` は Python の標準ライブラリなので、追加のインストールは不要です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import sys
```

---

## 2. 主な機能と使用例

### (1) コマンドライン引数の取得
Python スクリプトが実行されたときの引数を取得できます。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import sys

# コマンドライン引数の表示
print("コマンドライン引数:", sys.argv)

# 第一引数を取得
if len(sys.argv) > 1:
    print("第一引数:", sys.argv[1])
```

**使用例:**
`python script.py argument1 argument2` と実行すると、`sys.argv` で `['script.py', 'argument1', 'argument2']` が取得されます。

---

### (2) Python のバージョン情報の取得

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import sys

print("Python バージョン:", sys.version)
print("バージョン情報:", sys.version_info)
```

**使用例:**
特定の Python バージョンでスクリプトが実行されているかを確認する際に利用できます。

---

### (3) 標準入力・出力の操作

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import sys

# 標準出力のリダイレクト
sys.stdout.write("標準出力へのメッセージ\n")

# 標準入力の取得
print("入力を待機しています...")
user_input = sys.stdin.readline().strip()
print("入力された内容:", user_input)
```

**使用例:**
標準出力を別のファイルにリダイレクトすることも可能です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import sys

with open('output.txt', 'w') as f:
    sys.stdout = f
    print("このメッセージはファイルに出力されます")
    sys.stdout = sys.__stdout__
```

---

### (4) モジュール検索パスの確認と変更

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import sys

# 現在のモジュール検索パスを取得
print("モジュール検索パス:", sys.path)

# 新しいパスを追加
sys.path.append('/my/custom/path')
print("追加後のパス:", sys.path)
```

**使用例:**
カスタムモジュールが適切にインポートされるか確認する際に使用します。

---

### (5) インタープリタの終了

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import sys

print("プログラムを終了します。")
sys.exit(0)
```

**使用例:**
エラー発生時に `sys.exit(1)` で異常終了を明示できます。

---

### (6) 例外情報の取得

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import sys

try:
    1 / 0
except ZeroDivisionError:
    print("例外情報:", sys.exc_info())
```

**使用例:**
エラーハンドリング時に詳細な情報を取得したい場合に利用します。

---

### (7) メモリ使用量の取得

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import sys

x = [i for i in range(10000)]
print("リスト x のメモリ使用量:", sys.getsizeof(x), "バイト")
```

**使用例:**
変数がどれだけメモリを使用しているかを確認したいときに役立ちます。

---

### (8) 再帰制限の設定

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import sys

print("現在の再帰制限:", sys.getrecursionlimit())
sys.setrecursionlimit(2000)
print("変更後の再帰制限:", sys.getrecursionlimit())
```

**使用例:**
再帰的な処理を行う場合、デフォルトの制限を超えないよう調整できます。

---

## 3. `sys` vs `os` の比較

| 機能                     | `sys` | `os` |
|------------------------|------|------|
| コマンドライン引数の取得 | ✅ | ❌ |
| Python バージョン取得    | ✅ | ❌ |
| 標準入力・出力の操作    | ✅ | ❌ |
| モジュール検索パス管理   | ✅ | ❌ |
| メモリ使用量の取得     | ✅ | ❌ |
| システムコマンド実行    | ❌ | ✅ |

---

## まとめ
Python の `sys` ライブラリは、Python インタープリタと対話するための強力なツールです。特にコマンドライン引数の処理、バージョン確認、標準入出力の管理において便利です。Python スクリプトをより柔軟に制御するために、ぜひ活用してください！ 🚀