---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250314163344.png
date: 2025-03-14
hatena_path: /entry/2025/03/14/163414
slug: 管理を自動化するpython-shutil-ライブラリ
summary: Python 標準ライブラリの shutil は、ファイルやディレクトリの操作を簡単に行うためのツールを提供します。本記事では、shutil の主要な機能とその活用方法について詳しく解説します。
title: Python shutil完全ガイド！ファイル操作を自動化する実践テクニック — OKPy
description: shutil を使ったファイル操作の自動化で時間を節約。コピー・移動・削除・圧縮など、実践的な使用例と注意点を解説。初心者から上級者まで対応。
seo_title: Pythonのshutil活用ガイド！ファイル自動化の実践テクニック
seo_description: shutil を使ったファイル自動化の実践テクニック。コピー・移動・削除・圧縮などの具体的な使用例と注意点を初心者向けに解説します。
---



# 管理を自動化するPython shutil ライブラリ

# Python `shutil` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250314163344.png)

Python 標準ライブラリの `shutil` は、ファイルやディレクトリの操作を簡単に行うためのツールを提供します。本記事では、`shutil` の主要な機能とその活用方法について詳しく解説します。

## 1. `shutil` ライブラリの概要

- `shutil` は、ファイルやディレクトリのコピー、移動、削除などの操作を簡単に行うための標準ライブラリです。
- OS に依存せずに動作し、シンプルな API でファイル管理を実現できます。
- バックアップや一時ファイルの操作、自動化スクリプトに役立ちます。

### **インストール方法**
`shutil` は Python の標準ライブラリなので、追加のインストールは不要です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import shutil
```

---

## 2. 主な機能と使用例

### (1) ファイルのコピー（`copy`, `copy2`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import shutil

shutil.copy("source.txt", "destination.txt")  # 内容のみコピー
shutil.copy2("source.txt", "destination2.txt")  # メタデータもコピー
```

**使用例:**
ファイルをコピーし、バックアップやファイル管理を簡単に行う。

---

### (2) ディレクトリのコピー（`copytree`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import shutil

shutil.copytree("source_dir", "destination_dir")
```

**使用例:**
ディレクトリ全体をコピーして、フォルダのバックアップを作成する。

---

### (3) ファイルの移動・名前変更（`move`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import shutil

shutil.move("old_name.txt", "new_name.txt")
shutil.move("file.txt", "backup_folder/")
```

**使用例:**
ファイルの整理や、データの移動を簡単に行う。

---

### (4) ディレクトリの削除（`rmtree`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import shutil

shutil.rmtree("folder_to_delete")
```

**使用例:**
不要になったディレクトリを一括削除する。

---

### (5) ディスク容量の取得（`disk_usage`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import shutil

usage = shutil.disk_usage("/")
print(f"合計: {usage.total} バイト")
print(f"使用済み: {usage.used} バイト")
print(f"空き容量: {usage.free} バイト")
```

**使用例:**
ディスクの空き容量を確認し、ファイル操作を適切に管理する。

---

### (6) シンボリックリンクの作成（`symlink`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import os

os.symlink("source.txt", "symlink.txt")
```

**使用例:**
シンボリックリンクを作成し、元ファイルを変更せずに別の名前で参照できるようにする。

---

### (7) 一時ディレクトリの作成（`mkdtemp`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import tempfile

temp_dir = tempfile.mkdtemp()
print(f"作成された一時ディレクトリ: {temp_dir}")
```

**使用例:**
プログラム実行時に一時ディレクトリを作成し、不要になったら削除できる。

---

### (8) ファイルシステムの情報取得（`which`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import shutil

python_path = shutil.which("python")
print(f"Python の実行パス: {python_path}")
```

**使用例:**
特定のプログラムの実行パスを検索し、利用可能かを確認する。

---

### (9) ディレクトリの作成と削除（`mkdir` & `rmdir`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import os

os.mkdir("new_folder")
os.rmdir("new_folder")
```

**使用例:**
新しいディレクトリを作成し、不要になったら削除する。

---

### (10) ファイルの圧縮（`make_archive`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import shutil

shutil.make_archive("backup", "zip", "source_dir")
```

**使用例:**
ディレクトリを ZIP 形式に圧縮し、バックアップや配布用に活用する。

---

## 3. `shutil` の主な機能

| 機能                 | 説明 |
|------------------|------|
| `copy`          | ファイルをコピー（メタデータなし） |
| `copy2`         | ファイルをコピー（メタデータ付き） |
| `copytree`      | ディレクトリを再帰的にコピー |
| `move`          | ファイル・ディレクトリを移動 |
| `rmtree`        | ディレクトリを削除 |
| `disk_usage`    | ディスクの使用状況を取得 |

---

## まとめ
Python の `shutil` ライブラリを活用すると、ファイルやディレクトリの管理を簡単に自動化できます。バックアップ、整理、削除、ディスク容量の確認など、多くの用途に対応できるので、ぜひ `shutil` を活用して効率的なファイル管理を実現しましょう！ 🚀