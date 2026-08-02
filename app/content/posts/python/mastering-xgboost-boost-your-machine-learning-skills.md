---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250402095958.png
date: 2025-04-20
hatena_path: /entry/2025/04/20/161008
slug: mastering-xgboost-boost-your-machine-learning-skills
summary: xgboost は、勾配ブースティング（Gradient Boosting）アルゴリズムを高速・高精度に実装したライブラリです。Kaggle などの機械学習コンペティションでも頻繁に使用されており、分類・回帰タスクで高い性能を発揮します。本記事では、Python
  での xgboost の使い方を日本語で詳しく紹介します…
title: 'Mastering XGBoost: Boost Your Machine Learning Skills'
---

# Mastering XGBoost: Boost Your Machine Learning Skills

# Python `xgboost` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250402095958.png)

`xgboost` は、勾配ブースティング（Gradient Boosting）アルゴリズムを高速・高精度に実装したライブラリです。Kaggle などの機械学習コンペティションでも頻繁に使用されており、分類・回帰タスクで高い性能を発揮します。本記事では、Python での `xgboost` の使い方を日本語で詳しく紹介します。

## 1. `xgboost` の概要

- 勾配ブースティング（Gradient Boosting）法をベースとしたモデル。
- 並列学習、欠損値対応、クロスバリデーションなどを標準搭載。
- sklearn API とネイティブ API の両方に対応。

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install xgboost
```
</div>

---

## 2. 主な機能と使用例

### (1) ライブラリとデータセットの読み込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import xgboost as xgb
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42)
```
</div>

### (2) モデルの作成と学習（sklearn API）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
model.fit(X_train, y_train)
```
</div>

### (3) 予測と精度評価

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
```
</div>

### (4) 特徴量の重要度の可視化

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import matplotlib.pyplot as plt
xgb.plot_importance(model)
plt.show()
```
</div>

### (5) ハイパーパラメータの指定

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
model = xgb.XGBClassifier(max_depth=3, learning_rate=0.1, n_estimators=100, use_label_encoder=False, eval_metric='mlogloss')
model.fit(X_train, y_train)
```
</div>

### (6) クロスバリデーション（xgb.cv）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
dtrain = xgb.DMatrix(X_train, label=y_train)
params = {'objective': 'multi:softmax', 'num_class': 3}
cv_results = xgb.cv(params, dtrain, num_boost_round=10, nfold=3, metrics="mlogloss", seed=42)
print(cv_results)
```
</div>

### (7) DMatrix を使ったネイティブ API

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test)

params = {
    'objective': 'multi:softmax',
    'num_class': 3,
    'max_depth': 3,
    'eta': 0.1
}
model_native = xgb.train(params, dtrain, num_boost_round=50)
y_pred_native = model_native.predict(dtest)
```
</div>

### (8) モデルの保存と読み込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
model.save_model("xgb_model.json")
loaded_model = xgb.XGBClassifier()
loaded_model.load_model("xgb_model.json")
```
</div>

### (9) モデルの SHAP 値可視化（特徴量の寄与）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import shap
explainer = shap.Explainer(model)
shap_values = explainer(X_test)
shap.plots.beeswarm(shap_values)
```
</div>

### (10) 欠損値を含むデータの処理

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import numpy as np
X_train[0][0] = np.nan  # 欠損値を入れても自動処理される
model.fit(X_train, y_train)
```
</div>

---

## 3. `xgboost` の主な機能まとめ

| 機能 | 説明 |
|------|------|
| `XGBClassifier` / `XGBRegressor` | sklearn 互換のモデルクラス |
| `DMatrix` | 高速処理のためのデータ構造 |
| `cv` | クロスバリデーションの実行 |
| `plot_importance` | 特徴量の重要度を視覚化 |
| SHAP | 解釈可能性の高いモデル分析 |

---

## まとめ

`xgboost` は、高速かつ高精度なブースティング手法として、多くの現場で採用されています。分類・回帰・ランキングなど幅広いタスクに対応しており、特に構造化データに強みがあります。精度向上を目指すプロジェクトにはぜひ活用してみてください！