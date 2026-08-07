---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250321143123.png
date: 2025-03-21
hatena_path: /entry/2025/03/21/143148
slug: pythonのstatsmodelsライブラリ-統計モデリングとデータ分析の完全ガイド
summary: Python の statsmodels は、統計モデリングとデータ分析を行うための強力なライブラリです。本記事では、statsmodels の主な機能と使い方を、10個の具体的なコード例とともに紹介します。
title: Python statsmodelsの実践ガイド｜10コード例で学ぶ回帰分析・時系列解析 — OKPy
description: statsmodelsの使い方を、すぐに使える実践コード10個で完全網羅。回帰分析から時系列解析まで、複雑な統計処理も分かりやすく解説します。
seo_title: Python statsmodelsの実践ガイド｜10コード例で学ぶ回帰分析・時系列解析
seo_description: statsmodelsの使い方を、すぐに使える実践コード10個で完全網羅。回帰分析から時系列解析まで、複雑な統計処理も分かりやすく解説します。
---




# Pythonのstatsmodelsライブラリ:統計モデリングとデータ分析の完全ガイド

# Python `statsmodels` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250321143123.png)

Python の `statsmodels` は、統計モデリングとデータ分析を行うための強力なライブラリです。本記事では、`statsmodels` の主な機能と使い方を、10個の具体的なコード例とともに紹介します。

## 1. `statsmodels` ライブラリの概要

- 回帰分析、時系列解析、仮説検定、統計的検査などに対応。
- `NumPy` や `pandas` と連携しやすく、結果の可視化も可能。
- 計量経済学や統計学に基づいた解析をサポート。

### インストール方法
```bash
pip install statsmodels
```

---

## 2. 主な機能とソースコード例（10選）

### (1) 最小二乗法（OLS: Ordinary Least Squares）
```python
import statsmodels.api as sm
import numpy as np

x = np.array([1, 2, 3, 4, 5])
y = np.array([1, 2, 1.3, 3.75, 2.25])
x = sm.add_constant(x)
model = sm.OLS(y, x).fit()
print(model.summary())
```

### (2) ロジスティック回帰（Logit）
```python
x = np.array([1, 2, 3, 4, 5])
y = np.array([0, 0, 1, 1, 1])
x = sm.add_constant(x)
logit_model = sm.Logit(y, x).fit()
print(logit_model.summary())
```

### (3) 時系列モデル（ARIMA）
```python
import pandas as pd

data = pd.Series(np.random.randn(100))
model = sm.tsa.ARIMA(data, order=(1, 1, 1)).fit()
print(model.summary())
```

### (4) 仮説検定（T検定）
```python
from statsmodels.stats.weightstats import ttest_ind

a = np.random.normal(0, 1, 30)
b = np.random.normal(0.5, 1, 30)
result = ttest_ind(a, b)
print(result)
```

### (5) 一般化線形モデル（GLM）
```python
import statsmodels.formula.api as smf

data = {'x': [1,2,3,4,5], 'y': [1,3,4,6,8]}
model = smf.glm(formula='y ~ x', data=data, family=sm.families.Gaussian()).fit()
print(model.summary())
```

### (6) 主成分分析（PCA）
```python
from statsmodels.multivariate.pca import PCA

data = np.random.rand(100, 5)
pca = PCA(data, ncomp=2)
print(pca.factors)
```

### (7) バイナリアウトカムのプロビットモデル
```python
probit_model = sm.Probit(y, x).fit()
print(probit_model.summary())
```

### (8) 分散分析（ANOVA）
```python
from statsmodels.formula.api import ols
import pandas as pd

data = pd.DataFrame({
    'score': [90, 80, 75, 65, 70, 60],
    'group': ['A', 'A', 'B', 'B', 'C', 'C']
})
model = ols('score ~ C(group)', data=data).fit()
from statsmodels.stats.anova import anova_lm
anova_table = anova_lm(model)
print(anova_table)
```

### (9) QQプロット（正規性の検定）
```python
import matplotlib.pyplot as plt

data = np.random.normal(0, 1, 100)
sm.qqplot(data, line='s')
plt.show()
```

### (10) 自己相関プロット（ACF）
```python
from statsmodels.graphics.tsaplots import plot_acf

series = np.random.randn(100)
plot_acf(series, lags=20)
plt.show()
```

---

## 3. まとめ

`statsmodels` は、Python における高度な統計モデリングと推定分析に不可欠なライブラリです。各種回帰分析や時系列解析、統計的仮説検定まで、豊富な機能を簡単に活用することができます。

研究や業務で統計解析を必要とする方は、`statsmodels` を積極的に取り入れることでより質の高い分析が実現できます。📊