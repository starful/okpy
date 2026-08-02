---
title: 'PythonでサクッとモダンWeb UI構築！「NiceGUI」実践活用ガイド'
date: 2026-07-25
category: python
slug: nicegui
summary: '- **NiceGUI**は、HTML/CSS/JavaScriptを一切書かずにPythonコードだけでモダンなWeb UIを高速構築できるフレームワークです。 - FastAPI、Vue.js、Quasar、Socket.IOをベースにしており、Streamlitよりもきめ細やかなレイアウト制御とリアルタイム…'
lang: ja
---

# PythonでサクッとモダンWeb UI構築！「NiceGUI」実践活用ガイド

## TL;DR
- **NiceGUI**は、HTML/CSS/JavaScriptを一切書かずにPythonコードだけでモダンなWeb UIを高速構築できるフレームワークです。
- FastAPI、Vue.js、Quasar、Socket.IOをベースにしており、Streamlitよりもきめ細やかなレイアウト制御とリアルタイム双方向通信を実現します。
- 社内運用ツール、IoT/機器制御ダッシュボード、AI・データ分析のプロトタイピングなど、迅速な開発が求められる現場に最適です。

---

## 概要

PythonにおけるWeb UI構築ツールといえば、これまで Streamlit や Gradio、Dash などが主流でした。しかし、「レイアウトをもう少し細かく調整したい」「ボタンを押したときの挙動をより柔軟に記述したい」「画面全リロードによるチラつきを防ぎたい」といった不満を感じたことはないでしょうか？

**NiceGUI** は、そうした悩みを解決する新進気鋭のPython WebUIフレームワークです。

### NiceGUIの特徴と仕組み

NiceGUIは以下のようなスタックの上に乗っています。

- **バックエンド**: FastAPI（非同期処理とAPI管理）
- **フロントエンド**: Vue.js & Quasar Framework（モダンで美しいUIコンポーネント）
- **リアルタイム通信**: Socket.IO（WebSocketによる低遅延な双方向データ更新）

Python側でUIコンポーネント（ボタン、入力フォーム、グラフなど）を定義すると、WebSocketを介してフロントエンドのQuasarコンポーネントと自動的に同期されます。これにより、開発者はWebのフロントエンド技術（HTML/CSS/JS）を意識することなく、Pythonのロジック開発のみに集中できます。

### 他のフレームワークとの比較

| 項目 | Streamlit | Gradio | **NiceGUI** |
| :--- | :--- | :--- | :--- |
| **主な用途** | データ分析・ダッシュボード | MLモデルのデモ表示 | 社内ツール・IoT・汎用Webアプリ |
| **再描画モデル** | スクリプト全体を再実行 | 入力に応じたイベント定義 | **イベント駆動・リアルタイム同期** |
| **レイアウトの自由度** | 中程度（制約あり） | 低〜中程度 | **高（CSS/Flexbox/Grid対応）** |
| **実行速度/体感** | 状態変更時のリロード感あり | フォーム単位の実行 | **極めてスムーズ（WebSocket通信）** |
| **ベース技術** | 独自（Reactベース） | React | **FastAPI + Vue.js (Quasar)** |

特に「状態保持（State Management）」の扱いやすさと、「細かなUIイベントへの反応性」において、NiceGUIは他のツールより頭一つ抜けています。

---

## インストール

NiceGUIは `pip` から簡単にインストールできます。Python 3.8 以降が対応環境です。

```bash
pip install nicegui
```

もしグラフ描画（PlotlyやMatplotlibなど）や画像処理（Pillowなど）を組み合わせる場合は、関連ライブラリも合わせてインストールしておくと便利です。

```bash
pip install plotly pandas matplotlib pillow
```

---

## 基本サンプル

まずは最もシンプルなコードからスタートしましょう。ボタンをクリックするとカウンタがインクリメントされ、入力テキストがリアルタイムにラベルへ反映されるサンプルです。

```python
from nicegui import ui

# 状態管理用の変数
count = 0

def increment():
    global count
    count += 1
    counter_label.text = f'カウント: {count}'

# UIの構築
ui.label('NiceGUIへようこそ！').classes('text-2xl font-bold color-primary')

# テキスト入力とリアルタイムバインディング
input_field = ui.input(label='お名前を入力してください', placeholder='例: 山田太郎')
ui.label().bind_text_from(input_field, 'value', backward=lambda v: f'こんにちは、{v}さん！' if v else '')

# カウンターボタン
counter_label = ui.label('カウント: 0').classes('text-lg')
ui.button('カウントアップ', on_click=increment).props('icon=add color=positive')

# アプリの起動
ui.run(title='NiceGUI 基本サンプル', reload=True)
```

### コード解説
1. `ui.label()` や `ui.button()` などの関数を呼ぶだけで、画面にエレメントが配置されます。
2. `.classes()` メソッドに **Tailwind CSS** のクラス名を指定することで、スタイルを適用できます（例: `text-2xl`, `font-bold`）。
3. `.props()` メソッドを使って、ベースにある **Quasar** のプロパティ（アイコン設定やカラーテーマなど）を適用できます。
4. `bind_text_from` などのバインディング機能を使うと、ユーザーの入力と表示要素の同期を数行で記述可能です。
5. `ui.run(reload=True)` を設定すると、コード変更時に自動でブラウザがリロードされる開発モードで起動します。

---

## 実務で使えるコード例

実務の現場で直面する代表的な3つのユースケースを想定した、実践的なサンプルコードを紹介します。

### 1. リアルタイム・データ監視ダッシュボード（Plotly連携）

定期的にデータを取得・生成し、グラフと数値をリアルタイムに更新するIoT監視パネルやサーバーモニタリングのようなUIです。

```python
import random
from datetime import datetime
from nicegui import ui
import plotly.graph_objects as go

# 履歴データ
times = []
temperatures = []

# Plotlyの初期フィギュア作成
fig = go.Figure()
fig.add_trace(go.Scatter(x=times, y=temperatures, mode='lines+markers', name='温度 (°C)'))
fig.update_layout(
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis_title='時刻',
    yaxis_title='温度 (°C)',
    yaxis=dict(range=[10, 40])
)

# UIレイアウト
ui.label('リアルタイムセンサー・モニタリング').classes('text-xl font-bold mb-4')

with ui.row().classes('w-full items-center gap-4 mb-4'):
    with ui.card().classes('p-4 min-w-[200px] text-center'):
        ui.label('現在の温度').classes('text-sm text-gray-500')
        temp_label = ui.label('-- °C').classes('text-3xl font-bold text-blue-600')
    
    with ui.card().classes('p-4 min-w-[200px] text-center'):
        ui.label('ステータス').classes('text-sm text-gray-500')
        status_label = ui.label('待機中').classes('text-3xl font-bold text-gray-600')

# Plotlyグラフ要素の作成
plotly_chart = ui.plotly(fig).classes('w-full h-80')

def update_sensor_data():
    """センサーデータの模擬取得とUI更新"""
    now = datetime.now().strftime('%H:%M:%S')
    current_temp = round(random.uniform(18.0, 32.0), 1)

    # データを最新20件に制限
    times.append(now)
    temperatures.append(current_temp)
    if len(times) > 20:
        times.pop(0)
        temperatures.pop(0)

    # ラベル更新
    temp_label.text = f'{current_temp} °C'
    if current_temp > 28.0:
        status_label.text = '高温警告'
        status_label.classes(remove='text-gray-600 text-green-600', add='text-red-600')
    else:
        status_label.text = '正常'
        status_label.classes(remove='text-gray-600 text-red-600', add='text-green-600')

    # グラフデータ更新
    fig.data[0].x = times
    fig.data[0].y = temperatures
    plotly_chart.update()

# 2秒ごとに update_sensor_data を実行するタイマー
ui.timer(interval=2.0, callback=update_sensor_data)

ui.run(title='センサーダッシュボード', port=8080)
```

---

### 2. CSVファイルアップローダー & データ集計ツール（Pandas連携）

ユーザーがアップロードしたCSVファイルをPandasで読み込み、インタラクティブなテーブル表示と統計情報の計算を行うツールです。

```python
import io
import pandas as pd
from nicegui import events, ui

# 状態保持
df_holder = {'df': None}

ui.label('データ分析ツール').classes('text-2xl font-bold mb-4')

# アップロード完了時のハンドラ
def handle_upload(e: events.UploadEventArguments):
    try:
        # アップロードされたファイルをPandas DataFrameとして読み込む
        content = e.content.read()
        df = pd.read_csv(io.BytesIO(content))
        df_holder['df'] = df

        ui.notify(f'ファイル "{e.name}" の読み込みに成功しました', type='positive')
        render_data()
    except Exception as err:
        ui.notify(f'エラーが発生しました: {err}', type='negative')

# UI要素のプレースホルダー
upload_ui = ui.upload(
    label='CSVファイルをドロップまたは選択',
    on_upload=handle_upload,
    auto_upload=True
).props('accept=.csv').classes('w-full max-w-md mb-6')

data_container = ui.column().classes('w-full')

def render_data():
    """データテーブルと要約統計量をレンダリング"""
    data_container.clear()
    df = df_holder['df']
    if df is None:
        return

    with data_container:
        ui.label('データプレビュー').classes('text-lg font-bold mt-4')
        
        # AgGridやui.tableを使って表形式で表示
        columns = [{'name': col, 'label': col, 'field': col, 'sortable': True} for col in df.columns]
        rows = df.head(10).to_dict(orient='records')
        ui.table(columns=columns, rows=rows, row_key=df.columns[0]).classes('w-full')

        ui.label('基本統計量 (数値列)').classes('text-lg font-bold mt-6')
        stats_df = df.describe().reset_index()
        stats_columns = [{'name': col, 'label': col, 'field': col} for col in stats_df.columns]
        stats_rows = stats_df.to_dict(orient='records')
        ui.table(columns=stats_columns, rows=stats_rows, row_key='index').classes('w-full')

ui.run(title='CSVデータアナライザー')
```

---

### 3. ナビゲーションドロワー付き複数ページ構成＆ダークモード対応

実用的な社内ツールで求められる「サイドバーメニューによる画面切り替え」「ダークモード切替」「マルチページ構成」の雛形です。

```python
from nicegui import app, ui

# ダークモード設定の管理
dark_mode = ui.dark_mode()

# 共通ヘッダー・サイドバーの作成関数
def create_layout(title_text: str):
    with ui.header().classes('bg-primary text-white items-center justify-between'):
        with ui.row().classes('items-center'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
            ui.label(title_text).classes('text-xl font-bold ml-2')
        
        # ダークモード切替トグル
        with ui.row().classes('items-center gap-2'):
            ui.icon('light_mode')
            ui.switch(on_change=lambda e: dark_mode.set_value(e.value))
            ui.icon('dark_mode')

    with ui.left_drawer(value=True).classes('bg-slate-100 dark:bg-slate-800') as left_drawer:
        ui.label('メニュー').classes('text-xs text-gray-400 font-bold p-4 pb-1')
        with ui.column().classes('w-full gap-1 p-2'):
            ui.button('ダッシュボード', on_click=lambda: ui.navigate.to('/')).props('flat align=left').classes('w-full')
            ui.button('設定', on_click=lambda: ui.navigate.to('/settings')).props('flat align=left').classes('w-full')

# --- ページ1: ダッシュボード ---
@ui.page('/')
def main_page():
    create_layout('メインダッシュボード')
    with ui.column().classes('p-6'):
        ui.label('ようこそ、管理画面へ').classes('text-2xl font-bold')
        ui.label('ここにはメインの情報が表示されます。')

# --- ページ2: 設定画面 ---
@ui.page('/settings')
def settings_page():
    create_layout('システム設定')
    with ui.column().classes('p-6 max-w-lg gap-4'):
        ui.label('システムパラメータ設定').classes('text-2xl font-bold')
        
        ui.input(label='APIエンドポイント', value='https://api.example.com/v1')
        ui.select(label='ログレベル', options=['DEBUG', 'INFO', 'WARNING', 'ERROR'], value='INFO')
        ui.checkbox('詳細ログを有効化する', value=True)
        
        def save():
            ui.notify('設定を保存しました', type='positive')

        ui.button('保存する', on_click=save).props('color=primary')

ui.run(title='管理システム', port=8080)
```

---

## 注意点

NiceGUIは非常に強力ですが、アーキテクチャの特性上、いくつか注意すべきポイントがあります。

### 1. 状態（State）はサーバープロセス上に保持される
NiceGUIは、ユーザーごとのUIセッション状態をサーバー側のメモリ内で管理します。
- **利点**: クライアント・サーバー間のデータ同期コードを書かなくても、Python変数にアクセスするだけで画面が更新される。
- **注意点**: 接続ユーザー数が数百・数千に及ぶ大規模B2Cサービスには不向きです。メモリ使用量がスケールするため、主に**社内ツール、管理画面、プロトタイプ、組み込み用途**に向いています。

### 2. 重い同期処理（CPUバウンド/IOバウンド）による画面フリーズ
NiceGUIは FastAPI / `asyncio` のイベントループ上で動作しています。そのため、ボタンのクリックイベント内などで時間のかかる重い処理（大規模計算、同期的なWeb API呼出、時間のかかるDBクエリなど）をそのまま実行すると、**UI全体のレスポンスが停止（フリーズ）** します。

非同期処理を導入するか、後述の `run.cpu_bound` / `run.io_bound` を利用してスレッド/プロセスプールへ処理を逃がす必要があります。

### 3. クライアント固有の状態とグローバル状態の混同
複数ユーザーが同時にアクセスする場合、モジュールレベルのグローバル変数に状態を保持すると、**「Aさんの操作結果がBさんの画面にも反映されてしまう」** という問題が発生します。

ユーザーセッションごとに独立した状態を持たせる場合は、`@ui.page` のルーティング関数内で変数をローカル定義するか、`app.storage.user` などのストレージ機能を活用してください。

---

## FAQ (よくある質問)

### Q1. Streamlit や Gradio と比べてどのようなメリットがありますか？

**A.** 主に「細かなレイアウト調整の容易さ」「イベント駆動による操作性」「リアルタイム性」の3点がメリットです。

- **画面チラつきの無さ**: Streamlitは入力のたびにコード全体を先頭から再実行しますが、NiceGUIは変更があったコンポーネントだけをWebSocket経由で更新します。
- **自由度の高いレイアウト**: Tailwind CSSのクラスやFlex/Gridレイアウトが直感的に使え、Webデザイナーがいなくても見た目の整ったUIを作れます。
- **リアルタイム双方向通信**: バックエンド側で発生したデータ変化を `ui.timer` や非同期タスクを使って、ブラウザ側へ瞬時にPush通知・反映可能です。

---

### Q2. 重い処理（AI推論やDBアクセス）を実行するとUIが固まります。対処法は？

**A.** NiceGUIが提供している `run.cpu_bound` または `run.io_bound` を使用して、別スレッド/別プロセスで実行してください。

```python
import time
from nicegui import run, ui

def heavy_computation(x: int) -> int:
    """時間がかかる重い処理 (CPUバウンド)"""
    time.sleep(3)  # 擬似的な重い処理
    return x * 2

async def on_button_click():
    ui.notify('計算を開始しました...')
    # 別プロセスで実行し、UIスレッドをブロックしない
    result = await run.cpu_bound(heavy_computation, 21)
    ui.notify(f'計算完了！ 結果: {result}')

ui.button('重い処理を実行', on_click=on_button_click)
ui.run()
```

---

### Q3. 本番環境（Production）で運用・デプロイするにはどうすればよいですか？

**A.** Docker化するか、Linuxサーバー上で systemd または Gunicorn/Uvicorn を使用してプロセスを管理し、前段に Nginx などのリバースプロキシを配置するのが一般的です。

Nginx を設定する場合は、**WebSocket（`Upgrade` ヘッダー）を通す設定**を忘れないように注意してください。

**Nginx設定例（抜粋）:**
```nginx
location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

また、セッション永続化や設定ファイルの自動生成機能を活用すれば、Dockerコンテナ化も数行の `Dockerfile` で完結します。

---

## まとめ

NiceGUIは、「Pythonだけでアプリを作りたいが、Streamlitでは自由度が足りない」「Webフロントエンドの複雑なエコシステムに時間を取られたくない」と考えているPythonエンジニアにとって最高のソリューションです。

プロトタイピングの枠を超えて、現場でしっかり使える社内ツールやダッシュボードを驚くほどのスピードで構築できます。ぜひ次のプロジェクトで試してみてください！
