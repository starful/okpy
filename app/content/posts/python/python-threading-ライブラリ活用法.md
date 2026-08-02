---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250311115145.png
date: 2025-03-11
hatena_path: /entry/2025/03/11/201558
slug: python-threading-ライブラリ活用法
summary: Python 標準ライブラリの threading は、マルチスレッドプログラミングをサポートするためのツールを提供します。本記事では、threading
  の主要な機能とその活用方法について詳しく解説します。
title: Python threading ライブラリ活用法
---

# Python threading ライブラリ活用法

# Python `threading` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250311115145.png)

Python 標準ライブラリの `threading` は、マルチスレッドプログラミングをサポートするためのツールを提供します。本記事では、`threading` の主要な機能とその活用方法について詳しく解説します。

## 1. `threading` ライブラリの概要

- `threading` は、Python でマルチスレッドを利用するための標準ライブラリです。
- スレッドを使用することで、並行処理が可能になります。
- `GIL (Global Interpreter Lock)` の影響で CPU バウンドタスクでは効果が限定的ですが、I/O バウンドタスクには有効です。

### **インストール方法**
`threading` は Python の標準ライブラリなので、追加のインストールは不要です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import threading
```

---

## 2. 主な機能と使用例

### (1) 基本的なスレッドの作成（`Thread`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import threading
import time

def worker():
    print("スレッド開始")
    time.sleep(2)
    print("スレッド終了")

thread = threading.Thread(target=worker)
thread.start()
thread.join()  # メインスレッドでスレッドの完了を待つ
```

**使用例:**
バックグラウンドで処理を実行し、メインプログラムをブロックせずに処理できます。

---

### (2) スレッドのロック（`Lock`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import threading

lock = threading.Lock()
count = 0

def increment():
    global count
    with lock:
        for _ in range(100000):
            count += 1

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print("最終カウント:", count)
```

**使用例:**
複数のスレッドが同じデータにアクセスする際の競合を防ぐことができます。

---

### (3) イベントを使用したスレッドの制御（`Event`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import threading
import time

event = threading.Event()

def worker():
    print("待機中...")
    event.wait()
    print("処理開始！")

thread = threading.Thread(target=worker)
thread.start()
time.sleep(2)
event.set()  # スレッドを解放
```

**使用例:**
スレッドの開始を外部イベントで制御する場合に活用できます。

---

### (4) タスクのスケジューリング（`Timer`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import threading

def delayed_task():
    print("3秒後に実行されました！")

threading.Timer(3, delayed_task).start()
```

**使用例:**
一定時間後に特定のタスクを実行する場合に便利です。

---

### (5) 複数のタスクを管理（`ThreadPoolExecutor`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from concurrent.futures import ThreadPoolExecutor
import time

def worker(n):
    time.sleep(1)
    return f"完了: {n}"

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(worker, range(5))
    for result in results:
        print(result)
```

**使用例:**
スレッドプールを利用して複数のタスクを並列処理できます。

---

### (6) デーモンスレッドの作成（`daemon`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import threading
import time

def daemon_task():
    while True:
        print("デーモンスレッド動作中...")
        time.sleep(1)

daemon_thread = threading.Thread(target=daemon_task, daemon=True)
daemon_thread.start()
time.sleep(3)  # メインスレッドが終了すると、デーモンスレッドも終了
```

**使用例:**
バックグラウンドで動作するスレッドを作成し、メインスレッドの終了時に自動終了させる。

---

### (7) 条件変数を用いたスレッド同期（`Condition`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import threading

condition = threading.Condition()
shared_data = []

def producer():
    with condition:
        shared_data.append("データ")
        print("データを追加しました")
        condition.notify()

def consumer():
    with condition:
        condition.wait()
        print("データを取得しました:", shared_data.pop())

threading.Thread(target=consumer).start()
threading.Thread(target=producer).start()
```

**使用例:**
スレッド間でデータの受け渡しを制御する。

---

### (8) セマフォを用いたスレッド制限（`Semaphore`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import threading
import time

semaphore = threading.Semaphore(2)

def worker(n):
    with semaphore:
        print(f"スレッド {n} 開始")
        time.sleep(2)
        print(f"スレッド {n} 終了")

threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

**使用例:**
同時に実行できるスレッド数を制限する。

---

### (9) バリアを用いたスレッド同期（`Barrier`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import threading
import time

barrier = threading.Barrier(3)

def worker(n):
    print(f"スレッド {n} 待機中...")
    barrier.wait()
    print(f"スレッド {n} 実行開始")

threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

**使用例:**
複数のスレッドが同時に開始されるように同期する。

---

### (10) スレッドの識別子と名前を取得（`get_ident`, `current_thread`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import threading

def worker():
    print("スレッド ID:", threading.get_ident())
    print("スレッド名:", threading.current_thread().name)

thread = threading.Thread(target=worker, name="MyThread")
thread.start()
thread.join()
```

**使用例:**
スレッドのデバッグ時に ID や名前を取得する。

---

## 3. `threading` の主な機能

| 機能                 | 説明 |
|------------------|------|
| `Thread`         | スレッドの作成と実行 |
| `Lock`           | 排他制御のためのロック機構 |
| `Event`          | スレッドの同期と制御 |
| `Timer`          | 指定時間後にタスクを実行 |
| `ThreadPoolExecutor` | スレッドプールを使用して並列処理を管理 |

---

## まとめ
Python の `threading` ライブラリを活用すると、並行処理を簡単に実装できます。I/O バウンドのタスクやイベント駆動型のシステムで特に効果を発揮します。適切なスレッド管理を行い、効率的なマルチスレッド処理を実現しましょう！ 🚀