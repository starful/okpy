---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250303154126.png
date: 2025-03-03
hatena_path: /entry/2025/03/03/154158
slug: python-math-ライブラリ完全ガイド
summary: Python 標準ライブラリの math は、数学計算を簡単に行うための便利なツールです。本記事では、math ライブラリの基本概念から実践的な使用例までを詳しく解説します。
title: Python math ライブラリ完全ガイド
---

# Python math ライブラリ完全ガイド

# Python `math` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250303154126.png)

Python 標準ライブラリの `math` は、数学計算を簡単に行うための便利なツールです。本記事では、`math` ライブラリの基本概念から実践的な使用例までを詳しく解説します。

## 1. `math` ライブラリの概要

- `math` は、数学関連の基本的な関数を提供する標準ライブラリです。
- 三角関数、指数関数、対数関数、数値の丸め、特殊関数などを含みます。
- 浮動小数点演算を最適化するために使用されます。

### **インストール方法**
`math` は Python の標準ライブラリなので、追加のインストールは不要です。

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import math
```

---

## 2. 主な機能と使用例

### (1) 基本的な数学関数

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import math

# 絶対値
print("絶対値:", math.fabs(-10.5))

# 階乗
print("5の階乗:", math.factorial(5))

# 最大公約数
print("GCD(36, 60):", math.gcd(36, 60))
```

**使用例:**
統計計算やデータ処理でよく使用されます。

---

### (2) 三角関数

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import math

# 角度をラジアンに変換
angle = 45
rad = math.radians(angle)
print(f"{angle}度 -> {rad}ラジアン")

# 三角関数の計算
print("sin(45°):", math.sin(rad))
print("cos(45°):", math.cos(rad))
print("tan(45°):", math.tan(rad))
```

**使用例:**
物理計算や3Dグラフィックで使用されます。

---

### (3) 指数関数と対数関数

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import math

# 指数関数
print("e^2:", math.exp(2))

# 対数関数
print("log(8) (自然対数):", math.log(8))
print("log10(100):", math.log10(100))
```

**使用例:**
機械学習や統計モデルの計算で頻繁に使用されます。

---

### (4) 数値の丸めと近似

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import math

# 切り上げと切り捨て
print("ceil(3.4):", math.ceil(3.4))  # 4
print("floor(3.4):", math.floor(3.4))  # 3

# 四捨五入
print("round(3.567, 2):", round(3.567, 2))
```

**使用例:**
データのフォーマットや数値計算で活用されます。

---

### (5) 円周率と自然対数の底

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import math

print("円周率(π):", math.pi)
print("自然対数の底(e):", math.e)
```

**使用例:**
円の面積計算や指数関数の計算に使用されます。

---

### (6) 双曲線関数

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import math

# 双曲線関数の計算
print("sinh(1):", math.sinh(1))
print("cosh(1):", math.cosh(1))
print("tanh(1):", math.tanh(1))
```

**使用例:**
統計解析や信号処理で使用されます。

---

### (7) 座標変換（直交座標から極座標へ）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import math

x, y = 3, 4
r = math.hypot(x, y)
theta = math.atan2(y, x)
print("極座標 (r, θ):", r, theta)
```

**使用例:**
物理学やロボット工学の計算に利用されます。

---

### (8) 数値の分解

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import math

num = 123.456
frac, whole = math.modf(num)
print("整数部:", whole, "小数部:", frac)
```

**使用例:**
数値データの分離や分析に使用されます。

---

## 3. `math` vs `numpy` の比較

| 機能                      | `math` ライブラリ | `numpy` ライブラリ |
|-------------------------|---------------|-----------------|
| 基本的な数学関数         | ✅ | ✅ |
| 三角関数・対数関数       | ✅ | ✅ |
| 配列の計算              | ❌ | ✅ |
| ベクトル演算            | ❌ | ✅ |
| 高速な数値計算          | ❌ | ✅ |

---

## まとめ
Python の `math` ライブラリは、数学計算を簡単に行うための基本的なツールです。三角関数、指数関数、数値の丸めなど、日常的な計算に幅広く活用できます。より高度な計算を行いたい場合は `numpy` との組み合わせも検討してください！ 🚀