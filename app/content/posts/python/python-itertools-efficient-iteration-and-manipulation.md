---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250309105255.png
date: 2025-03-09
hatena_path: /entry/2025/03/09/105322
slug: python-itertools-efficient-iteration-and-manipulation
summary: Python 標準ライブラリの itertools は、反復処理（イテレーション）を効率的に行うための便利なツールを提供します。本記事では、itertools
  の主要な機能とその活用方法について詳しく解説します。
title: 'Python Itertools: Efficient Iteration and Manipulation'
---

# Python Itertools: Efficient Iteration and Manipulation

# Python `itertools` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250309105255.png)

Python 標準ライブラリの `itertools` は、反復処理（イテレーション）を効率的に行うための便利なツールを提供します。本記事では、`itertools` の主要な機能とその活用方法について詳しく解説します。

## 1. `itertools` ライブラリの概要

- `itertools` は、イテレータを操作するための関数を提供します。
- ループ処理を効率化し、メモリ効率の良いコードを記述するのに役立ちます。
- 組み合わせ・順列の生成、無限イテレータ、フィルタリング機能などを備えています。

### **インストール方法**
`itertools` は Python の標準ライブラリなので、追加のインストールは不要です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools
```

---

## 2. 主な機能と使用例

### (1) 無限イテレータ（`count`, `cycle`, `repeat`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools

# count: 1 ずつ増加する無限ループ
take_5 = list(itertools.islice(itertools.count(10, 2), 5))
print(take_5)  # [10, 12, 14, 16, 18]

# cycle: 指定したシーケンスを無限ループ
cycler = itertools.cycle(["A", "B", "C"])
print([next(cycler) for _ in range(6)])  # ['A', 'B', 'C', 'A', 'B', 'C']

# repeat: 同じ値を繰り返す
print(list(itertools.repeat("X", 4)))  # ['X', 'X', 'X', 'X']
```

**使用例:**
`count` はインデックス生成に、`cycle` はラウンドロビン処理に、`repeat` はデフォルト値の設定に役立ちます。

---

### (2) 順列と組み合わせの生成（`permutations`, `combinations`, `combinations_with_replacement`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools

items = ['A', 'B', 'C']

# 順列（並べ替え）
print(list(itertools.permutations(items, 2)))  # [('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]

# 組み合わせ（順番は考慮しない）
print(list(itertools.combinations(items, 2)))  # [('A', 'B'), ('A', 'C'), ('B', 'C')]

# 重複を許可する組み合わせ
print(list(itertools.combinations_with_replacement(items, 2)))  # [('A', 'A'), ('A', 'B'), ('A', 'C'), ('B', 'B'), ('B', 'C'), ('C', 'C')]
```

**使用例:**
組み合わせ最適化やパスワードクラッキングのシミュレーションに利用できます。

---

### (3) フィルタリング（`filterfalse`, `dropwhile`, `takewhile`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools

nums = [1, 2, 3, 4, 5, 6]

# 条件に合わないものを抽出（偶数を抽出）
print(list(itertools.filterfalse(lambda x: x % 2, nums)))  # [2, 4, 6]

# 条件が True の間スキップ
print(list(itertools.dropwhile(lambda x: x < 4, nums)))  # [4, 5, 6]

# 条件が True の間取得
print(list(itertools.takewhile(lambda x: x < 4, nums)))  # [1, 2, 3]
```

**使用例:**
条件に基づいてリストから要素を効率的にフィルタリングできます。

---

### (4) 要素のグループ化（`groupby`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools

data = [("A", 1), ("A", 2), ("B", 3), ("B", 4), ("C", 5)]

for key, group in itertools.groupby(data, key=lambda x: x[0]):
    print(key, list(group))
```

**使用例:**
ソート済みデータをグループ化し、カテゴリ別に処理するのに役立ちます。

---

### (5) 連結したイテレータの生成（`chain`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools

list1 = [1, 2, 3]
list2 = [4, 5, 6]

# 2つのリストを連結
print(list(itertools.chain(list1, list2)))  # [1, 2, 3, 4, 5, 6]
```

**使用例:**
複数のリストやイテレータを1つにまとめる際に利用できます。

---

### (6) 複数イテレータの直積（`product`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools

colors = ["red", "blue"]
sizes = ["S", "M", "L"]

# 直積を生成
print(list(itertools.product(colors, sizes)))
```

**使用例:**
全パターンの組み合わせ（例: 商品オプション）を生成する際に活用できます。

---

### (7) 値の累積和（`accumulate`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools

numbers = [1, 2, 3, 4]
print(list(itertools.accumulate(numbers)))  # [1, 3, 6, 10]
```

**使用例:**
データの累積計算（例: 売上合計）に活用できます。

---

### (8) 指定回数イテレータを繰り返す（`tee`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools

iterator = iter([1, 2, 3])
iter1, iter2 = itertools.tee(iterator, 2)

print(list(iter1))  # [1, 2, 3]
print(list(iter2))  # [1, 2, 3]
```

**使用例:**
同じイテレータを複数回利用する場合に活用できます。

---

### (9) 指定回数の繰り返し（`starmap`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools
import operator

pairs = [(1, 2), (3, 4), (5, 6)]
print(list(itertools.starmap(operator.mul, pairs)))  # [2, 12, 30]
```

**使用例:**
関数をリストの各ペアに適用する際に活用できます。

---

### (10) 指定回数でイテレータを分割（`batched`）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import itertools

# Python 3.10 以降で利用可能
def batched(iterable, n):
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch

print(list(batched(range(10), 3)))  # [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]
```

**使用例:**
データを一定サイズごとに分割する際に活用できます。

---

## まとめ
Python の `itertools` ライブラリは、反復処理を効率的に行うための強力なツールです。無限イテレータ、組み合わせ・順列、フィルタリング、グループ化など、さまざまなシナリオで活用できます。ぜひ、あなたのコードに活かしてみてください！ 🚀