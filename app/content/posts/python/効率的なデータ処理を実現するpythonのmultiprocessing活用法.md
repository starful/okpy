---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250311182457.png
date: 2025-03-12
hatena_path: /entry/2025/03/12/092101
slug: 効率的なデータ処理を実現するpythonのmultiprocessing活用法
summary: Python 標準ライブラリの multiprocessing は、マルチプロセスを活用して並列処理を実現するためのツールを提供します。本記事では、multiprocessing
  の主要な機能とその活用方法について詳しく解説します。
title: Python multiprocessingの使い方｜マルチプロセス並列処理でデータ処理を高速化
description: Pythonのmultiprocessingモジュールを使ったマルチプロセス並列処理の基本とデータ処理高速化の手法を解説。Poolクラスの使い方、threadingとの違い、CPUバウンドな処理の効率化テクニックまで具体的なコード例付きで分かりやすく紹介します。
seo_title: Python multiprocessingの使い方｜マルチプロセス並列処理でデータ処理を高速化 — OKPy
seo_description: Pythonのmultiprocessingモジュールを使ったマルチプロセス並列処理の基本とデータ処理高速化の手法を解説。Poolクラスの使い方、threadingとの違い、CPUバウンドな処理の効率化テクニックまで具体的なコード例付きで分かりやすく紹介します。
---


# 効率的なデータ処理を実現するPythonのmultiprocessing活用法

# Python `multiprocessing` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250311182457.png)

Python 標準ライブラリの `multiprocessing` は、マルチプロセスを活用して並列処理を実現するためのツールを提供します。本記事では、`multiprocessing` の主要な機能とその活用方法について詳しく解説します。

## 1. `multiprocessing` ライブラリの概要

- `multiprocessing` は、複数のプロセスを並列に実行するための標準ライブラリです。
- `threading` と異なり、`multiprocessing` は **GIL (Global Interpreter Lock)** の制約を受けません。
- CPU バウンドのタスク（数値計算、データ処理など）に適しています。

### **インストール方法**
`multiprocessing` は Python の標準ライブラリなので、追加のインストールは不要です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing
```

---

## 2. 主な機能と使用例

### (1) 基本的なプロセスの作成（`Process`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing
import time

def worker():
    print("プロセス開始")
    time.sleep(2)
    print("プロセス終了")

if __name__ == "__main__":
    process = multiprocessing.Process(target=worker)
    process.start()
    process.join()
```

**使用例:**
独立したプロセスを作成し、バックグラウンドでタスクを実行できます。

---

### (2) 複数プロセスの並列実行（`Pool`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing

def square(n):
    return n * n

if __name__ == "__main__":
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(square, range(10))
        print(results)
```

**使用例:**
大量のデータを並列処理する際に有効です。

---

### (3) プロセス間でデータを共有（`Queue`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing

def worker(q):
    q.put("データ送信")

if __name__ == "__main__":
    q = multiprocessing.Queue()
    process = multiprocessing.Process(target=worker, args=(q,))
    process.start()
    process.join()
    print("受信したデータ:", q.get())
```

**使用例:**
プロセス間でデータを安全に共有できます。

---

### (4) 共有メモリ（`Value` と `Array`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing

def worker(val):
    val.value += 1

if __name__ == "__main__":
    val = multiprocessing.Value("i", 0)
    process = multiprocessing.Process(target=worker, args=(val,))
    process.start()
    process.join()
    print("更新後の値:", val.value)
```

**使用例:**
プロセス間で共有メモリを使用することで、データのやり取りが可能です。

---

### (5) プロセスの同期（`Lock`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing
import time

def worker(lock):
    with lock:
        print("ロック取得")
        time.sleep(1)
        print("ロック解放")

if __name__ == "__main__":
    lock = multiprocessing.Lock()
    processes = [multiprocessing.Process(target=worker, args=(lock,)) for _ in range(3)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
```

**使用例:**
複数のプロセスが同じリソースにアクセスする際の競合を防ぐ。

---

### (6) マネージャーを用いたデータ共有（`Manager`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing

def worker(shared_list):
    shared_list.append("データ追加")

if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        shared_list = manager.list()
        process = multiprocessing.Process(target=worker, args=(shared_list,))
        process.start()
        process.join()
        print("共有リスト:", list(shared_list))
```

**使用例:**
複数のプロセス間でリストや辞書などのデータを共有できます。

---

### (7) イベントを用いたプロセス制御（`Event`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing
import time

event = multiprocessing.Event()

def worker():
    print("待機中...")
    event.wait()
    print("実行開始！")

if __name__ == "__main__":
    process = multiprocessing.Process(target=worker)
    process.start()
    time.sleep(2)
    event.set()
    process.join()
```

**使用例:**
プロセスの開始をイベントで制御する。

---

### (8) セマフォを用いたプロセス制限（`Semaphore`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing
import time

semaphore = multiprocessing.Semaphore(2)

def worker(n):
    with semaphore:
        print(f"プロセス {n} 開始")
        time.sleep(2)
        print(f"プロセス {n} 終了")

if __name__ == "__main__":
    processes = [multiprocessing.Process(target=worker, args=(i,)) for i in range(5)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
```

**使用例:**
同時に実行できるプロセス数を制限する。

---

### (9) バリアを用いたプロセス同期（`Barrier`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing
import time

barrier = multiprocessing.Barrier(3)

def worker(n):
    print(f"プロセス {n} 待機中...")
    barrier.wait()
    print(f"プロセス {n} 実行開始")

if __name__ == "__main__":
    processes = [multiprocessing.Process(target=worker, args=(i,)) for i in range(3)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
```

**使用例:**
複数のプロセスが同時に開始されるように同期する。

---

### (10) プロセスの識別子を取得（`current_process`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import multiprocessing

def worker():
    print("プロセス ID:", multiprocessing.current_process().pid)

if __name__ == "__main__":
    process = multiprocessing.Process(target=worker)
    process.start()
    process.join()
```

**使用例:**
プロセスのデバッグ時に ID を取得する。

---

## 3. `multiprocessing` の主な機能

| 機能                 | 説明 |
|------------------|------|
| `Process`         | 独立したプロセスを作成し実行 |
| `Pool`           | 並列処理用のワーカープール |
| `Queue`          | プロセス間通信に使用するキュー |
| `Value` / `Array` | 共有メモリを利用したデータ共有 |
| `Lock`           | 排他制御のためのロック機構 |

---

## まとめ
Python の `multiprocessing` ライブラリを活用すると、GIL の制約を受けずに並列処理を実行できます。データ処理や並列タスク管理に適しており、効率的なマルチプロセス処理を実現できます。🚀