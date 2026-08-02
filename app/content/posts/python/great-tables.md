---
title: 'Great Tables実践ガイド：Pythonで美しい表を作る'
date: 2026-07-30
category: python
slug: great-tables
summary: '- Great Tablesはpandas/polarsのDataFrameをR言語の`gt`パッケージ相当の美しいHTML/PNG表に変換するPythonライブラリ - `GT()`にDataFrameを渡し、`.tab_header()`や`.fmt_number()`などのメソッドをチェーンするだけで、レポ…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260730135507.jpg'
lang: ja
---

# Great Tables実践ガイド：Pythonで美しい表を作る

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260730135507.jpg)


## TL;DR
- Great Tablesはpandas/polarsのDataFrameをR言語の`gt`パッケージ相当の美しいHTML/PNG表に変換するPythonライブラリ
- `GT()`にDataFrameを渡し、`.tab_header()`や`.fmt_number()`などのメソッドをチェーンするだけで、レポートやダッシュボード品質の表がすぐ作れる
- Jupyter Notebook、静的HTMLレポート、PDF出力（Quarto経由）など幅広い用途に対応し、matplotlibやplotlyと組み合わせたデータ可視化レポートの「表」パートを大幅に強化できる

## 概要

データ分析の現場では、グラフだけでなく「表」を見やすく整形する需要が非常に高い。売上ランキング、KPIサマリー、比較表など、数値を正確に、かつ視覚的にわかりやすく提示したい場面は多い。しかし、pandasの`DataFrame.to_html()`やExcelへの単純な貼り付けでは、条件付き書式やヒートマップ的な強調、桁区切り・単位付きフォーマットなどを実現するのに手間がかかる。

Great Tablesは、Rコミュニティで人気の高い`gt`パッケージの設計思想をPythonに移植したライブラリで、2023年にPosit（旧RStudio）出身のメンバーらによって公開された。「データの表現に関する文法（Grammar of Tables）」という考え方に基づき、ヘッダー・本体・フッターといった表の構成要素を宣言的に組み立てていく。matplotlibのように低レベルな描画を意識する必要がなく、pandasやpolarsのDataFrameを渡してメソッドチェーンで装飾していくだけで、業務レポートにそのまま使える品質の表が完成する。

出力形式はHTML（Jupyter Notebook内でのインライン表示、Webレポート埋め込み）に加え、PNG画像へのエクスポートにも対応しており、Slack通知やメール添付、静的レポートPDFへの埋め込みなど、実務での応用範囲が広い。

## インストール

pipまたはcondaで導入できる。pandas・polarsどちらのDataFrameにも対応しているため、既存の分析環境に追加するだけで利用可能。

```bash
pip install great_tables
```

PNG画像へのエクスポート機能（`GT.save()`）を使う場合は、内部でSeleniumベースのレンダリングを利用するため、追加の依存関係が必要になることがある。

```bash
pip install "great_tables[extra]"
```

Jupyter Notebook上での利用が中心であれば、`jupyter`や`ipykernel`もあわせてインストールしておくとよい。

```bash
pip install great_tables pandas polars jupyterlab
```

## 基本サンプル

まずは架空の月次売上データを使って、基本的な表を作成する流れを見ていく。

```python
import pandas as pd
from great_tables import GT, md, html

# サンプルデータ：地域別・商品別の月次売上
df = pd.DataFrame({
    "region": ["東京", "大阪", "福岡", "札幌"],
    "product": ["プランA", "プランA", "プランB", "プランB"],
    "sales": [1_250_000, 980_000, 640_000, 410_000],
    "growth": [0.12, -0.03, 0.08, 0.21],
    "target_rate": [0.95, 0.80, 1.10, 0.68],
})

gt_tbl = (
    GT(df)
    .tab_header(
        title="2026年7月 月次売上レポート",
        subtitle="地域別・商品別サマリー"
    )
    .fmt_currency(columns="sales", currency="JPY", decimals=0)
    .fmt_percent(columns=["growth", "target_rate"], decimals=1)
    .cols_label(
        region="地域",
        product="商品",
        sales="売上高",
        growth="前月比",
        target_rate="目標達成率",
    )
    .tab_source_note(source_note="社内販売管理システムより集計")
)

gt_tbl
```

Jupyter Notebook上でこのオブジェクトを評価すると、整形済みの表がインラインで表示される。`.fmt_currency()`で通貨単位付きの数値フォーマットを、`.fmt_percent()`でパーセント表示を自動化しており、手動で文字列結合する必要がない点が便利だ。

### 条件付き書式で強調する

実務では「目標未達の行を赤く強調したい」といったニーズが頻出する。Great Tablesでは`.tab_style()`と`loc.body()`を組み合わせることで、条件に応じたセルの装飾ができる。

```python
from great_tables import loc, style

gt_tbl_styled = (
    gt_tbl
    .tab_style(
        style=style.fill(color="#ffe5e5"),
        locations=loc.body(
            columns="target_rate",
            rows=df["target_rate"] < 1.0
        )
    )
    .tab_style(
        style=style.text(color="#1a7a1a", weight="bold"),
        locations=loc.body(
            columns="growth",
            rows=df["growth"] > 0
        )
    )
)

gt_tbl_styled
```

さらに、数値の大小を棒グラフ的に可視化したい場合は`.data_color()`を使うとヒートマップ表現が簡単に実現できる。

```python
gt_tbl_heat = gt_tbl.data_color(
    columns="sales",
    palette=["#f7fbff", "#08519c"],
    domain=[df["sales"].min(), df["sales"].max()],
)

gt_tbl_heat
```

### PNGとして書き出す

Slack通知やメール添付など、静止画として共有したい場合は`save()`メソッドでPNGに書き出せる。

```python
gt_tbl_styled.save("sales_report_202607.png", scale=2)
```

`scale`パラメータで解像度を調整できるため、印刷用途など高精細さが必要な場面にも対応できる。

## 注意点

- **PNG出力には追加依存が必要**：`save()`によるPNGエクスポートは内部でヘッドレスブラウザ相当のレンダリングエンジンを使用するため、環境によっては初回実行時にドライバのダウンロードが発生し、CI環境などでは事前準備が必要になる。
- **列の型に敏感**：`.fmt_currency()`や`.fmt_percent()`などのフォーマッタは数値型（int/float）の列にのみ適用できる。文字列型のまま渡すとエラーになるため、事前に`pd.to_numeric()`などで型を揃えておく必要がある。
- **大量行の表には不向き**：Great Tablesは「見せるための表」を作る用途に最適化されており、数千〜数万行規模のデータをそのまま表示する用途には向かない。事前に集計・グルーピングしてから渡すのが基本的な使い方になる。
- **バージョン間でAPIが変化しやすい**：まだ比較的新しいライブラリであり、メジャーバージョンアップ時にメソッド名や引数仕様が変更されることがある。本番運用に組み込む場合は、`requirements.txt`でバージョンを固定しておくことを推奨する。
- **日本語フォントの扱い**：PNG出力時に日本語が文字化けする、あるいは表示されないケースがある。この場合はHTMLテンプレート側でWebフォント（Noto Sans JPなど）を明示的に指定するか、`.opt_table_font()`でフォントファミリーを指定して回避する。

```python
gt_tbl_jp = gt_tbl.opt_table_font(font="Noto Sans JP")
```

- **polars利用時の列参照**：polarsのDataFrameを使う場合、Expressionベースの操作とGreat Tables側のAPIが混在しないよう注意する。基本的にGreat Tablesに渡す前に集計・整形を完了させ、GT側では表示装飾に専念する設計が安全。

## FAQ

**Q1. pandasの`.style`（Styler）と何が違うのですか？**

A. pandasの`Styler`はDataFrame表示にCSSベースの装飾を加える軽量な仕組みだが、あくまで「装飾」の域を出ない。一方Great Tablesは、ヘッダー・スパナー（列グループ見出し）・フッター・ソースノートといった表の構造そのものを宣言的に定義できる「表専用の文法」を持っており、より複雑なレポート的表現（結合ヘッダー、単位付きフォーマット、脚注管理など）を体系的に扱える点が異なる。単純な強調表示だけならStylerで十分だが、公開資料やレポートとしての完成度を求めるならGreat Tablesが適している。

**Q2. matplotlibやplotlyのグラフと組み合わせて使えますか？**

A. 直接的にグラフオブジェクトを埋め込む機能はないが、実務ではよく「グラフはplotly、数値サマリー表はGreat Tables」という役割分担でレポートを構成する。両方をHTMLとして書き出し、同一のNotebookやWebページ内に並べて配置するのが一般的な運用パターンだ。また、`.fmt_nanoplot()`という機能を使うと、セル内に小さなスパークライン風のミニグラフを直接埋め込むことも可能で、時系列の推移を1セルで表現したい場合に有効。

```python
gt_tbl.fmt_nanoplot(columns="monthly_trend")
```

**Q3. Great Tablesで作った表をQuartoやPDFレポートに組み込めますか？**

A. 可能。Great TablesはPositのQuartoエコシステムとの親和性を意識して設計されており、Quarto文書内のPythonチャンクでGTオブジェクトを返すだけで、HTML出力・PDF出力の両方にレンダリングされる（PDF出力時は内部でHTMLからの変換またはPNG埋め込みが行われる）。Quartoを使わない場合でも、`GT`オブジェクトの`.as_raw_html()`メソッドで生のHTML文字列を取得できるため、既存のHTMLレポート生成パイプラインやメールテンプレートに組み込むことも容易だ。

---

Great Tablesは、「グラフは得意だが表はいつも素朴なままだった」という分析者にとって、レポートの完成度を一段引き上げるための実用的な選択肢になる。まずは既存の集計結果に`GT()`をかぶせてみるところから試してみるとよい。
