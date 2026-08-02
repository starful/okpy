---
title: 'Marimo実践ガイド：リアクティブなPythonノートブックで再現性の高い分析環境を作る'
date: 2026-07-27
category: python
slug: marimo
summary: '- Marimoはセルの依存関係を自動追跡する「リアクティブ」なPythonノートブックで、隠れた状態を排除できる - ノートブックファイルが純粋な`.py`として保存されるため、Gitでの差分管理やコードレビューがしやすい - `marimo run`でノートブックをそのままWebアプリ化でき、UIウィジェット…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260727064420.jpg'
lang: ja
---

# Marimo実践ガイド：リアクティブなPythonノートブックで再現性の高い分析環境を作る

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260727064420.jpg)


## TL;DR
- Marimoはセルの依存関係を自動追跡する「リアクティブ」なPythonノートブックで、隠れた状態を排除できる
- ノートブックファイルが純粋な`.py`として保存されるため、Gitでの差分管理やコードレビューがしやすい
- `marimo run`でノートブックをそのままWebアプリ化でき、UIウィジェットとの連携も標準サポート

## 概要

Jupyter Notebookは長年データ分析やプロトタイピングの標準ツールとして使われてきましたが、「セルの実行順序に依存した隠れた状態」「変数の再定義による混乱」「`.ipynb`形式のJSONがGit差分と相性が悪い」といった課題が根強く指摘されてきました。

**Marimo**は、これらの課題を解決するために設計されたオープンソースのPythonノートブックです。最大の特徴は、あるセルの変数を変更すると、それに依存する他のセルが自動的に再実行される「リアクティブプログラミングモデル」を採用している点です。これにより、セルをどの順番で実行しても常に一貫した結果が得られます。

さらに、ノートブックは内部的にはただのPythonファイル（`.py`）として保存されるため、`git diff`で変更内容が読みやすく、`black`や`ruff`などの通常のPythonツールチェーンにもそのまま乗せられます。スライダーやドロップダウンなどのUIウィジェットも組み込みで用意されており、`marimo run`コマンド一つでノートブックをインタラクティブなWebアプリケーションとして公開できるのも大きな強みです。

社内ダッシュボードの試作、機械学習の実験管理、データ探索レポートの共有など、実務のさまざまな場面で活用できます。

## インストール

Marimoは`pip`または`uv`でインストールできます。

```bash
# pipの場合
pip install marimo

# uvの場合（高速）
uv pip install marimo

# インストール確認
marimo --version
```

追加でグラフ描画やデータ処理を行う場合は、以下もあわせてインストールしておくと便利です。

```bash
pip install marimo pandas matplotlib altair polars
```

インストール後、以下のコマンドでチュートリアル用ノートブックを起動して動作確認ができます。

```bash
marimo tutorial intro
```

## 基本サンプル

### 新規ノートブックの作成と起動

```bash
marimo edit my_notebook.py
```

このコマンドを実行すると、ブラウザが自動的に開き、Marimoのセル編集UIが表示されます。存在しないファイル名を指定した場合は、新規ノートブックとして作成されます。

### リアクティブな依存関係の基本

Marimoの核心はセル間の自動依存解決です。以下は3つのセルからなるシンプルな例です。

```python
# セル1: データの読み込み
import pandas as pd

df = pd.read_csv("sales.csv")
```

```python
# セル2: フィルタ条件（UIスライダーと連動）
import marimo as mo

min_amount = mo.ui.slider(0, 10000, value=1000, label="最低売上金額")
min_amount
```

```python
# セル3: フィルタ結果の表示
filtered_df = df[df["amount"] >= min_amount.value]
filtered_df
```

ここでポイントとなるのは、セル2の`min_amount`スライダーを動かすと、Marimoが「`min_amount.value`を参照しているセル3」を自動的に検出して再実行してくれることです。Jupyterのように手動で再実行する必要はありません。逆に、セル1の`df`を変更すれば、それに依存するセル3も自動的に更新されます。

### 実務的なコード例：CSVデータの探索ダッシュボード

以下は、実際の業務でよくある「CSVをアップロードして条件を変えながら集計結果を確認する」ダッシュボードの例です。

```python
import marimo as mo
import pandas as pd
import altair as alt

# ファイルアップロードUI
file_upload = mo.ui.file(filetypes=[".csv"], label="CSVファイルをアップロード")
file_upload
```

```python
# アップロードされたファイルを読み込む
mo.stop(file_upload.value is None, mo.md("ファイルをアップロードしてください"))

df = pd.read_csv(file_upload.contents())
df.head()
```

```python
# 集計軸を選択するUI
group_col = mo.ui.dropdown(
    options=df.select_dtypes(include="object").columns.tolist(),
    label="集計軸を選択"
)
metric_col = mo.ui.dropdown(
    options=df.select_dtypes(include="number").columns.tolist(),
    label="集計対象の数値列"
)
mo.hstack([group_col, metric_col])
```

```python
# 集計結果とグラフの表示
mo.stop(group_col.value is None or metric_col.value is None)

summary = (
    df.groupby(group_col.value)[metric_col.value]
    .agg(["sum", "mean", "count"])
    .reset_index()
    .sort_values("sum", ascending=False)
)

chart = alt.Chart(summary).mark_bar().encode(
    x=alt.X(group_col.value, sort="-y"),
    y="sum",
)

mo.vstack([summary, chart])
```

この例では`mo.stop()`を使い、必要な入力が揃っていない場合に後続セルの実行を止めています。これはMarimoでよく使う実務パターンで、UIの状態に応じたガード処理を簡潔に書けます。

### Webアプリとして公開する

作成したノートブックはそのままアプリとして配布できます。

```bash
marimo run my_notebook.py --port 8080
```

このコマンドを実行すると、コード編集UIを含まない、エンドユーザー向けの実行専用画面が起動します。社内向けの簡易ツールや分析レポートの共有に便利です。

### 通常のPythonスクリプトとしての実行

Marimoノートブックは通常の`.py`ファイルなので、CIパイプラインなどでは以下のようにスクリプトとして直接実行することも可能です。

```bash
python my_notebook.py
```

## 注意点

実務でMarimoを導入する際に押さえておくべき点をまとめます。

1. **グローバル変数の再代入は禁止される**
   Marimoでは、同じ変数名を複数のセルで定義することができません（Jupyterでは許容されていた挙動です）。これはリアクティブな依存グラフを構築するための制約であり、意図的な設計です。既存のJupyterノートブックを移行する際は、変数名の重複がないか事前に整理する必要があります。

2. **重い処理の自動再実行によるコスト**
   依存関係にあるセルは変更のたびに自動再実行されるため、大きなデータ読み込みや重いモデル学習を含むセルは意図せず何度も走ることがあります。`mo.ui.run_button()`で明示的なトリガー式にする、あるいは`@mo.cache`（またはPython標準の`functools.lru_cache`）でキャッシュするなどの対策が推奨されます。

3. **循環参照はエラーになる**
   セルAがセルBに依存し、セルBがセルAに依存するような循環関係を作ると、Marimoは実行前にエラーとして検出します。依存関係の設計はシンプルなDAG（有向非巡回グラフ）を意識する必要があります。

4. **既存のJupyter資産との互換性**
   `.ipynb`ファイルはMarimoの`.py`形式に変換するコマンド（`marimo convert`）が用意されていますが、マジックコマンド（`%%time`など）やセル出力の一部は自動移行できない場合があります。移行後は必ず目視での確認が必要です。

5. **チーム展開時のバージョン管理**
   Marimoは開発速度が非常に速いライブラリのため、破壊的変更が入ることがあります。チームで利用する場合は`requirements.txt`やpyprojectで`marimo`のバージョンを固定し、アップデート時は変更履歴（CHANGELOG）を確認することを推奨します。

## FAQ

**Q1. JupyterノートブックからMarimoへ簡単に移行できますか？**

A. `marimo convert notebook.ipynb -o notebook.py`コマンドで自動変換が可能です。ただし、前述の通り変数名の重複や特殊なマジックコマンドを使っている場合は手動での調整が必要になります。特に、EDA（探索的データ分析）で同じ変数名（`df`や`result`など）を使い回している既存ノートブックは、移行時にセルの再構成が発生しやすいので注意してください。

**Q2. MarimoとJupyterはどちらを使うべきですか？**

A. 用途によります。使い捨ての試行錯誤やチュートリアル的な用途、既存のJupyter拡張機能（特定のKernelやウィジェット）に強く依存している場合はJupyterが無難です。一方、複数人でのレビューを前提としたコード、ダッシュボードとしての配布、再現性の担保が重要なプロジェクト（実験管理やレポート自動生成など）では、Gitとの親和性やリアクティブ実行の恩恵が大きいMarimoが適しています。

**Q3. 機械学習の実験管理にMarimoは使えますか？**

A. 使えます。ハイパーパラメータをUIスライダーで調整しながらモデルの評価指標をリアルタイムに確認する、といった用途に特に向いています。ただし、学習処理自体は前述の通り重い処理なので、`mo.ui.run_button()`で「学習開始」ボタンを明示的に配置し、意図しない自動再学習を防ぐ設計にすることをおすすめします。またMLflowやWeights & Biasesといった既存の実験管理ツールとは役割が異なり、Marimoはあくまで「対話的な実験環境」を提供するものなので、長期的な実験履歴の保存・比較は専用ツールと併用するのが実務的です。
