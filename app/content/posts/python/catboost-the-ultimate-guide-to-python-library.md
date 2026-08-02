---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250415185029.png
date: 2025-04-15
hatena_path: /entry/2025/04/15/185304
slug: catboost-the-ultimate-guide-to-python-library
summary: catboost は、Yandex によって開発された、特にカテゴリ変数（categorical features）の処理に強い勾配ブースティング（Gradient
  Boosting）ライブラリです。前処理が最小限で済み、高速かつ高精度な学習が可能なことから、実務でも広く使われています。本記事では、Python での …
title: 'catboost: The Ultimate Guide to Python Library'
---

# catboost: The Ultimate Guide to Python Library

# Python `catboost` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250415185029.png)

`catboost` は、Yandex によって開発された、特にカテゴリ変数（categorical features）の処理に強い勾配ブースティング（Gradient Boosting）ライブラリです。前処理が最小限で済み、高速かつ高精度な学習が可能なことから、実務でも広く使われています。本記事では、Python での `catboost` の使い方を日本語で紹介します。

## 1. `catboost` の概要

- カテゴリ変数を自動的に処理可能（エンコーディング不要）。
- 欠損値の自動処理に対応。
- GPU 対応、sklearn API 互換。
- 高精度・高汎化性のモデル構築に優れる。

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install catboost
```
</div>

---

## 2. 主な機能と使用例

### (1) データの読み込みと準備

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

# サンプルデータ（カテゴリ変数含む）
data = pd.DataFrame({
    '色': ['赤', '青', '赤', '緑'],
    'サイズ': ['S', 'M', 'L', 'S'],
    '重さ': [1.0, 2.5, 3.0, 1.2],
    'クラス': [0, 1, 1, 0]
})

X = data.drop('クラス', axis=1)
y = data['クラス']
cat_features = [0, 1]  # カテゴリ変数の列番号
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```
</div>

### (2) モデルの作成と学習

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
model = CatBoostClassifier(verbose=0)
model.fit(X_train, y_train, cat_features=cat_features)
```
</div>

### (3) 予測と評価

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
```
</div>

### (4) モデルの保存と読み込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
model.save_model("catboost_model.cbm")
model.load_model("catboost_model.cbm")
```
</div>

### (5) 特徴量の重要度の表示

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import matplotlib.pyplot as plt
import seaborn as sns

importances = model.get_feature_importance()
feature_names = X.columns
sns.barplot(x=importances, y=feature_names)
plt.title("Feature Importance")
plt.show()
```
</div>

### (6) SHAP による特徴量の可視化

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
explainer = model.get_feature_importance(type="ShapValues")
print(explainer)
```
</div>

### (7) sklearn API の利用

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from catboost import CatBoostClassifier
model = CatBoostClassifier(iterations=100, depth=4, learning_rate=0.1, loss_function='Logloss', verbose=0)
model.fit(X_train, y_train, cat_features=cat_features)
```
</div>

### (8) GPU を使った高速学習

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
model = CatBoostClassifier(task_type='GPU', devices='0', verbose=0)
model.fit(X_train, y_train, cat_features=cat_features)
```
</div>

### (9) 欠損値を含むデータの自動処理

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
X_train.iloc[0, 0] = None
model.fit(X_train, y_train, cat_features=cat_features)
```
</div>

### (10) モデルの可視化（ツリービュー）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from catboost.utils import get_roc_curve
from sklearn.metrics import roc_auc_score

curve = get_roc_curve(model, Pool(X_test, y_test, cat_features=cat_features))
print("ROC AUC:", roc_auc_score(y_test, model.predict_proba(X_test)[:,1]))
```
</div>

---

## 3. `catboost` の主な機能まとめ

| 機能 | 説明 |
|------|------|
| カテゴリ変数対応 | 自動的にカテゴリ変数を処理（エンコード不要） |
| 欠損値処理 | 特別な前処理なしで対応 |
| 高速学習 | GPU 対応、効率的なアルゴリズム構造 |
| sklearn 互換 | `fit`, `predict`, `score` が利用可能 |
| SHAP / 可視化 | モデルの解釈性にも対応 |

---

## まとめ

`catboost` は、特にカテゴリデータの多い構造化データを扱う機械学習プロジェクトにおいて強力なツールです。学習効率、予測精度、前処理の簡潔さを重視する場合には非常に有用なライブラリです。