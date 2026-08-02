---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250310160357.png
date: 2025-03-10
hatena_path: /entry/2025/03/10/160422
slug: python-functools-ライブラリの活用方法
summary: Python 標準ライブラリの functools は、関数プログラミングをより効果的に行うためのツールを提供します。本記事では、functools
  の主要な機能とその活用方法について詳しく解説します。
title: Python functools ライブラリの活用方法
---

# Python functools ライブラリの活用方法

# Python `functools` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250310160357.png)

Python 標準ライブラリの `functools` は、関数プログラミングをより効果的に行うためのツールを提供します。本記事では、`functools` の主要な機能とその活用方法について詳しく解説します。

## 1. `functools` ライブラリの概要

- `functools` は、関数を操作・最適化するためのツールを提供します。
- 高階関数（関数を引数や戻り値として扱う関数）を簡単に扱うことができます。
- キャッシュ、部分適用、比較関数、デコレーターの作成などに役立ちます。

### **インストール方法**
`functools` は Python の標準ライブラリなので、追加のインストールは不要です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools
```

---

## 2. 主な機能と使用例

### (1) 関数の結果をキャッシュ（`lru_cache`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools
import time

@functools.lru_cache(maxsize=3)
def slow_function(n):
    time.sleep(2)  # 処理を遅らせる
    return n * n

print(slow_function(2))  # 計算に2秒かかる
print(slow_function(2))  # キャッシュされて即座に返される
```

**使用例:**
頻繁に呼び出される計算処理をキャッシュして高速化できます。

---

### (2) 関数の引数を固定する（`partial`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools

def power(base, exponent):
    return base ** exponent

square = functools.partial(power, exponent=2)
print(square(3))  # 9
```

**使用例:**
特定の引数を固定した関数を作成し、コードの再利用性を向上させます。

---

### (3) 関数のメタデータを保持（`wraps`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("実行前")
        result = func(*args, **kwargs)
        print("実行後")
        return result
    return wrapper

@my_decorator
def say_hello():
    "この関数は挨拶をする"
    print("Hello!")

print(say_hello.__name__)  # 'say_hello' （デコレーターを使用しても関数名が保持される）
```

**使用例:**
デコレーターを適用した関数のメタデータを保持し、デバッグを容易にします。

---

### (4) 関数を連続適用（`reduce`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools
import operator

numbers = [1, 2, 3, 4]
result = functools.reduce(operator.mul, numbers)
print(result)  # 24（1 * 2 * 3 * 4）
```

**使用例:**
リストの全要素に対して累積計算を行う際に便利です。

---

### (5) 比較可能なクラスを作成（`total_ordering`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools

@functools.total_ordering
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __eq__(self, other):
        return self.age == other.age
    
    def __lt__(self, other):
        return self.age < other.age

p1 = Person("Alice", 30)
p2 = Person("Bob", 25)
print(p1 > p2)  # True
```

**使用例:**
比較演算子（`<`, `<=`, `>`, `>=`）を簡単に定義できます。

---

### (6) デコレーターを適用した関数のキャッシュクリア（`cache_clear`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools

@functools.lru_cache(maxsize=3)
def square(n):
    return n * n

square(2)
square.cache_clear()  # キャッシュをクリア
```

**使用例:**
キャッシュをクリアして、新しいデータを強制的に再計算できます。

---

### (7) 複数の比較キーを適用（`cmp_to_key`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools

def compare(x, y):
    return x - y

sorted_list = sorted([5, 3, 8, 1], key=functools.cmp_to_key(compare))
print(sorted_list)  # [1, 3, 5, 8]
```

**使用例:**
カスタム比較関数をソートに適用できます。

---

### (8) デフォルト引数を固定した関数の作成（`partialmethod`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools

class Calculator:
    def power(self, base, exponent):
        return base ** exponent
    
    square = functools.partialmethod(power, exponent=2)

calc = Calculator()
print(calc.square(4))  # 16
```

**使用例:**
クラス内で引数を固定したメソッドを作成できます。

---

### (9) 関数の呼び出し回数を制限（`cache`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools

@functools.cache
def factorial(n):
    return n * factorial(n - 1) if n else 1

print(factorial(5))  # 120
```

**使用例:**
再帰関数の計算結果をキャッシュして、高速化できます。

---

### (10) クロージャのデータを保持（`update_wrapper`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import functools

def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return functools.update_wrapper(wrapper, func)

@decorator
def say_hello():
    "挨拶をする関数"
    print("Hello!")

print(say_hello.__doc__)  # 挨拶をする関数
```

**使用例:**
デコレーターが元の関数のメタデータを保持するようにできます。

---

## 3. `functools` の便利な機能

| 機能                 | 説明 |
|------------------|------|
| `lru_cache`      | 関数の結果をキャッシュして再計算を防ぐ |
| `partial`        | 引数を固定した関数を作成する |
| `wraps`          | デコレーターを適用した関数のメタデータを保持する |
| `reduce`         | 連続して計算を適用し、リストの要素を集約する |

---

## まとめ
Python の `functools` ライブラリは、関数を効率的に扱うための強力なツールです。キャッシュ、部分適用、デコレーター、累積計算など、さまざまなシナリオで活用できます。ぜひ、あなたのプロジェクトに `functools` を活かしてみてください！ 🚀