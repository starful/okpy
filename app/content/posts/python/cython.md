---
title: 'Cython実践ガイド：Pythonコードを高速化する'
date: 2026-08-01
category: python
slug: cython
summary: '- CythonはPythonに近い文法でC拡張モジュールを書けるコンパイラ兼言語で、型宣言を追加するだけでループ処理を数十倍高速化できる。 - `pip install cython` で導入でき、`.pyx` ファイルを `cythonize` でビルドするだけで既存のPythonコードをほぼそのまま高速化で…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260801100340.jpg'
lang: ja
---

# Cython実践ガイド：Pythonコードを高速化する

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260801100340.jpg)


## TL;DR（3行）

- CythonはPythonに近い文法でC拡張モジュールを書けるコンパイラ兼言語で、型宣言を追加するだけでループ処理を数十倍高速化できる。
- `pip install cython` で導入でき、`.pyx` ファイルを `cythonize` でビルドするだけで既存のPythonコードをほぼそのまま高速化できる。
- 効果を最大化するには `cdef` による型宣言、NumPy配列には `memoryview`、境界チェック無効化などの最適化オプションを組み合わせる必要がある。

## 概要

Cythonは、Pythonのスーパーセット言語であり、Pythonコードに静的型情報を追加してC言語にコンパイルすることで、実行速度を大幅に向上させるツールです。NumPyやpandas、scikit-learnといった主要なPythonライブラリの内部でも広く使われており、「Pythonの書きやすさ」と「Cの実行速度」の両立を目的としています。

Cythonが特に効果を発揮するのは以下のようなケースです。

- 数値計算のforループなど、CPythonのインタプリタオーバーヘッドがボトルネックになっている処理
- NumPy配列に対する要素単位のアクセスを大量に行う処理
- 既存のC/C++ライブラリをPythonから呼び出したい場合（ラッパー作成）
- GIL（Global Interpreter Lock）を解放して並列処理を行いたい場合

一方で、NumPyのベクトル化演算のようにすでに最適化されたAPIを呼び出しているだけの処理では、Cython化の恩恵は小さくなります。まずは `cProfile` などでボトルネックを特定してから適用するのが実務上のセオリーです。

## インストール

Cythonは通常のPythonパッケージとして `pip` からインストールできます。C言語のコンパイラ（Linux/macOSでは `gcc` や `clang`、WindowsではVisual Studio Build Tools）が事前に必要です。

```bash
# Cython本体のインストール
pip install cython

# ビルドに必要なツールも合わせて入れておくと安心
pip install setuptools wheel numpy
```

macOSの場合、Xcodeコマンドラインツールが入っていないとコンパイルに失敗するため、事前に以下を実行しておきます。

```bash
xcode-select --install
```

インストール後、以下のコマンドでバージョンを確認できます。

```bash
cython --version
```

## 基本サンプル

### 1. 最小構成のCythonモジュール

Cythonのコードは `.pyx` 拡張子で書きます。まずはPythonの整数演算を高速化する簡単な例です。

```cython
# fib.pyx
def fib(int n):
    cdef int a = 0
    cdef int b = 1
    cdef int i
    for i in range(n):
        a, b = b, a + b
    return a
```

`cdef` はC言語相当の変数を宣言するキーワードで、これによりPythonオブジェクトのオーバーヘッドを排除し、ループ内の演算がCレベルの速度で実行されます。

### 2. ビルド設定（setup.py）

`.pyx` ファイルをビルドするための `setup.py` を用意します。

```python
# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="fib_module",
    ext_modules=cythonize("fib.pyx", compiler_directives={"language_level": "3"}),
)
```

ビルドは以下のコマンドで実行します。

```bash
python setup.py build_ext --inplace
```

成功すると `fib.cpython-3xx-darwin.so`（macOSの場合）のような共有ライブラリが生成され、通常のPythonモジュールと同じように `import` できます。

```python
import fib
print(fib.fib(30))  # 832040
```

### 3. pyximportによる簡易実行

開発中はビルド手順を省略し、`pyximport` でその場コンパイルすることも可能です。

```python
import pyximport
pyximport.install(language_level=3)
import fib

print(fib.fib(20))
```

小規模な検証や個人利用には便利ですが、本番運用では明示的な `setup.py` ビルドを推奨します。

### 4. NumPy配列を高速に処理する実務例

Cythonの真価は、NumPy配列への要素アクセスを伴うループ処理で発揮されます。以下は2つの配列の要素ごとの距離計算を行う例です。

```cython
# distance.pyx
import numpy as np
cimport numpy as cnp
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def euclidean_distances(cnp.ndarray[cnp.float64_t, ndim=1] x,
                         cnp.ndarray[cnp.float64_t, ndim=1] y):
    cdef Py_ssize_t n = x.shape[0]
    cdef cnp.ndarray[cnp.float64_t, ndim=1] result = np.empty(n, dtype=np.float64)
    cdef Py_ssize_t i
    cdef double diff

    for i in range(n):
        diff = x[i] - y[i]
        result[i] = diff * diff

    return result
```

ここで使っている `@cython.boundscheck(False)` と `@cython.wraparound(False)` は、配列の境界チェックと負のインデックス対応を無効化するディレクティブです。安全性は下がりますが、ループのたびに行われる検証コストがなくなるため、体感速度が大きく変わります。

対応する `setup.py` はNumPyのヘッダーを含める必要があります。

```python
# setup.py
from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules=cythonize("distance.pyx", compiler_directives={"language_level": "3"}),
    include_dirs=[np.get_include()],
)
```

### 5. 型付きmemoryviewを使う（推奨パターン）

`cnp.ndarray` の代わりに、より汎用的な「型付きmemoryview」を使うと、NumPy配列以外（`array.array` など）にも対応でき、可読性も向上します。実務ではこちらが推奨されることが多いです。

```cython
# moving_average.pyx
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def moving_average(double[:] values, int window):
    cdef Py_ssize_t n = values.shape[0]
    cdef Py_ssize_t i, j
    cdef double total
    cdef double[:] result = values.copy()

    for i in range(window - 1, n):
        total = 0.0
        for j in range(i - window + 1, i + 1):
            total += values[j]
        result[i] = total / window

    return result
```

## 注意点

- **型宣言をサボると効果が薄い**：`.pyx` にしただけで `cdef` を一切使わない場合、純粋なPythonとほぼ同じ速度しか出ません。ボトルネック箇所には必ず型を明示しましょう。
- **境界チェック無効化は諸刃の剣**：`boundscheck(False)` などを設定した状態で配列の範囲外アクセスが起きると、例外にならずセグメンテーションフォールトでプロセスごと落ちることがあります。十分にテストしてから本番コードへ適用してください。
- **デバッグがしづらい**：CythonコードはCにコンパイルされるため、通常のPythonデバッガでは追いにくくなります。`cython -a fib.pyx` で生成されるHTMLアノテーション（黄色が濃いほどPython呼び出しが多く低速）を使い、最適化箇所を可視化するのが有効です。
- **ビルド環境への依存**：配布先の環境にCコンパイラや同一OS/アーキテクチャの互換性が必要です。配布パッケージには `manylinux` ホイールなどのビルド済みバイナリを用意するか、ソース配布に `cythonize` の依存を明記する必要があります。
- **GILの扱いに注意**：並列化のために `nogil` ブロックを使う場合、その中でPythonオブジェクト（リストや辞書、`str` など）を触るとクラッシュや未定義動作の原因になります。純粋なCレベルの型のみで完結させる必要があります。
- **言語レベルの明示を忘れない**：`language_level` を指定しないとPython 2互換モードで解釈され、意図しない挙動（`print` の扱いなど）になることがあります。常に `"3"` を明示しましょう。

## FAQ

**Q1. CythonとNumbaはどちらを使うべきですか？**

用途によります。Numbaは既存のPython関数に `@njit` デコレータを付けるだけで手軽にJITコンパイルできるため、プロトタイピングや単発の高速化に向いています。一方Cythonはビルド工程が必要な分、C/C++ライブラリとの連携、ビルド済みパッケージとしての配布、Pythonオブジェクトとの細かい相互運用が必要な場面で強みを発揮します。長期運用するライブラリの一部としてはCython、社内スクリプトの一時的な高速化にはNumba、という使い分けが実務では一般的です。

**Q2. `cdef` と `cpdef` の違いは何ですか？**

`def` はPythonから呼び出せる通常の関数、`cdef` はC言語レベルの関数でPythonからは直接呼び出せません（呼び出しオーバーヘッドがない分高速）。`cpdef` はその中間で、Cython内部からはCレベルの高速呼び出し、Python側からは通常のPython関数として呼び出せるハイブリッド関数を定義できます。モジュール内部でのみ使う高速化対象の補助関数は `cdef`、外部に公開したい高速関数は `cpdef` にするのが基本方針です。

**Q3. 既存のPythonコードをそのまま`.pyx`にリネームするだけで速くなりますか？**

多少は速くなります。`.py` ファイルをそのまま `.pyx` としてコンパイルするだけでも、Pythonバイトコードのインタプリタオーバーヘッドの一部が削減され、体感で1〜2割程度高速化することがあります。ただし本格的な高速化（数倍〜数十倍）を得るには、ボトルネックとなるループや変数に `cdef` で型を付け、NumPy配列アクセスには memoryview を使うといった作業が不可欠です。まずはプロファイラでホットスポットを特定し、そこだけを段階的にCython化していくアプローチが効率的です。
