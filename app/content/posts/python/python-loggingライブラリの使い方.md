---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250313104428.png
date: 2025-03-13
hatena_path: /entry/2025/03/13/104509
slug: python-loggingライブラリの使い方
summary: Python 標準ライブラリの logging は、アプリケーションのログを記録・管理するためのツールを提供します。本記事では、logging の主要な機能とその活用方法について詳しく解説します。
title: Python loggingライブラリの使い方
---

# Python loggingライブラリの使い方

# Python `logging` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250313104428.png)

Python 標準ライブラリの `logging` は、アプリケーションのログを記録・管理するためのツールを提供します。本記事では、`logging` の主要な機能とその活用方法について詳しく解説します。

## 1. `logging` ライブラリの概要

- `logging` は、Python 標準のログ記録ライブラリです。
- デバッグ、情報、警告、エラー、重大なエラーなど、異なるレベルのログを記録できます。
- ファイルへの出力、コンソール出力、リモート送信など、柔軟なログ管理が可能です。

### **インストール方法**
`logging` は Python の標準ライブラリなので、追加のインストールは不要です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging
```

---

## 2. 主な機能と使用例

### (1) 基本的なログの出力（`basicConfig`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.info("これは情報ログです。")
```

**使用例:**
シンプルなログを記録し、デバッグやエラーの追跡に活用できます。

---

### (2) ログの詳細なフォーマット設定

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logging.debug("デバッグメッセージ")
logging.info("情報メッセージ")
```

**使用例:**
ログのフォーマットを設定し、時刻やログレベルを含めた詳細なログを記録できます。

---

### (3) ファイルにログを保存

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging

logging.basicConfig(
    filename='app.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logging.warning("これは警告ログです。")
```

**使用例:**
ログをファイルに保存し、後から分析できるようにします。

---

### (4) 例外情報をログに記録

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging

try:
    1 / 0
except ZeroDivisionError:
    logging.exception("ゼロ除算エラーが発生しました！")
```

**使用例:**
例外発生時にスタックトレースを含めたログを記録できます。

---

### (5) ロガーの作成と使用（`getLogger`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging

logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.debug("デバッグメッセージ")
```

**使用例:**
カスタムロガーを作成し、モジュールごとにログの管理を分けることができます。

---

### (6) 異なるレベルのログを記録

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.debug("デバッグメッセージ")
logging.info("情報メッセージ")
logging.warning("警告メッセージ")
logging.error("エラーメッセージ")
logging.critical("重大なエラーメッセージ")
```

**使用例:**
異なるログレベルを適切に活用して、システムの状態を記録する。

---

### (7) ログの回転保存（`RotatingFileHandler`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler("app.log", maxBytes=1000, backupCount=3)
logger = logging.getLogger("my_logger")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

for i in range(100):
    logger.info(f"ログメッセージ {i}")
```

**使用例:**
ログファイルのサイズが一定を超えたら、自動的に新しいファイルを作成する。

---

### (8) 日時でログを分割（`TimedRotatingFileHandler`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging
from logging.handlers import TimedRotatingFileHandler

handler = TimedRotatingFileHandler("timed_app.log", when="midnight", interval=1, backupCount=7)
logger = logging.getLogger("timed_logger")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("このログは日付ごとに新しいファイルに保存されます。")
```

**使用例:**
ログを日次や週次などで自動的にローテーションする。

---

### (9) JSON 形式でログを出力

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage()
        }
        return json.dumps(log_record)

logger = logging.getLogger("json_logger")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("JSON 形式のログメッセージ")
```

**使用例:**
ログを JSON 形式で出力し、構造化ログとして管理する。

---

### (10) メールでエラーログを送信（`SMTPHandler`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import logging
from logging.handlers import SMTPHandler

mail_handler = SMTPHandler(
    mailhost=("smtp.example.com", 587),
    fromaddr="noreply@example.com",
    toaddrs=["admin@example.com"],
    subject="アプリケーションエラー",
    credentials=("user", "password"),
    secure=()
)

logger = logging.getLogger("email_logger")
logger.addHandler(mail_handler)
logger.setLevel(logging.ERROR)

logger.error("重大なエラーが発生しました！")
```

**使用例:**
エラー発生時に管理者へ自動でメール通知を送る。

---

## 3. `logging` の主な機能

| 機能                 | 説明 |
|------------------|------|
| `basicConfig`      | ログの基本設定を行う |
| `getLogger`        | カスタムロガーを作成する |
| `StreamHandler`    | コンソールにログを出力する |
| `FileHandler`      | ファイルにログを保存する |
| `Formatter`        | ログのフォーマットを設定する |

---

## まとめ
Python の `logging` ライブラリを活用すると、アプリケーションのログ管理を柔軟に行うことができます。デバッグ、エラーハンドリング、ファイル保存など、さまざまな用途で活用できるので、ぜひ `logging` を使いこなしましょう！ 🚀