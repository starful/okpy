---
title: 'Pythonで構築する次世代TUI：Textualによる実践ターミナルUI開発ガイド'
date: 2026-07-22
category: python
slug: textual
summary: '- Textualは、PythonでWebアプリケーションのように美しい「TUI（Terminal User Interface）」を構築できるモダンな非同期フレームワークです。 - CSSに似たスタイリング（TCSS）、コンポーネント指向のWidget設計、強力なイベント駆動モデルにより、複雑なデスクトップ級ア…'
lang: ja
---

# Pythonで構築する次世代TUI：Textualによる実践ターミナルUI開発ガイド

## TL;DR
- Textualは、PythonでWebアプリケーションのように美しい「TUI（Terminal User Interface）」を構築できるモダンな非同期フレームワークです。
- CSSに似たスタイリング（TCSS）、コンポーネント指向のWidget設計、強力なイベント駆動モデルにより、複雑なデスクトップ級アプリをターミナル上に構築できます。
- 本記事では、基礎から「実務で使えるリアルタイム・システム＆ログ監視ダッシュボード」の実装まで、コード付きで徹底解説します。

---

## 1. 概要：なぜ今Textualなのか？

CLI（Command Line Interface）ツールは軽量で高速ですが、複雑な情報の表示や複数操作の並行処理には限界があります。一方でGUIやWebアプリを立ち上げるのは、SSH経由のサーバー作業やローカルの軽量ツールにおいてはオーバースペックな場合があります。

その架け橋となるのが **TUI（Terminal User Interface）** であり、現在最も洗練されたPython TUIフレームワークが **Textual** です。

Textualは、ターミナル出力美化ライブラリとして有名な `Rich` の開発者（Will McGugan氏）によって作られました。Richが「テキストの装飾やレイアウトの出力」を担当するのに対し、Textualは「マウス操作、キーボード入力、非同期イベント処理、状態管理を備えたフル機能のUIフレームワーク」を提供します。

### Textualの主な特徴
1. **コンポーネント指向のアーキテクチャ**: ReactやVueのようにWidgetを組み合わせて画面を構築します。
2. **TCSS（Textual CSS）**: CSSに極めて近い記法で、レイアウト（Flexbox, Grid）、色、余白、アニメーションを定義できます。
3. **完全非同期（async/await）ベース**: asyncioの上に構築されており、UI描画をブロックせずにバックグラウンドで重い処理を実行できます。
4. **リアクティブ（Reactive）プロパティ**: 変数の値が変更されると、依存するUIが自動的に再描画されます。
5. **クロスプラットフォーム＆マウス対応**: macOS, Linux, Windows Terminalで動作し、クリックやスクロール操作にも対応します。

---

## 2. インストールと開発環境のセットアップ

Textualは Python 3.8 以降に対応しています。まずはライブラリ本体と、開発時に便利な開発者ツールをインストールします。

```bash
# 本体および標準Widgetのインストール
pip install textual

# 開発用ツール（デバッグコンソール等）のインストール
pip install textual-dev
```

### 開発用コンソール（Textual Console）の活用
Textual開発では、アプリの画面出力とログ（print文やデバッグログ）を分離するために、別ウィンドウで開発コンソールを立ち上げることができます。

ターミナルを2つ開き、以下のように実行します。

**ターミナル1（デバッグログ表示用）:**
```bash
textual console
```

**ターミnal2（アプリ実行用）:**
```bash
textual run --dev main.py
```

これにより、アプリのUIを崩すことなく `self.log()` による出力や例外のスタックトレースをターミナル1でリアルタイムに確認できます。

---

## 3. 基本サンプル：カウンターアプリで理解する構成要素

まずは、Textualの基本構造を理解するために「カウンターアプリ」を作成します。ボタンを押すと数値が増減するシンプルなアプリです。

### `basic_counter.py`

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static
from textual.reactive import reactive
from textual.containers import Horizontal, Vertical

class CounterWidget(Static):
    """カウンターを表示・操作するカスタムWidget"""
    
    # リアクティブプロパティ。値が変わると自動的にUIが更新される
    count = reactive(0)

    def watch_count(self, old_value: int, new_value: int) -> None:
        """countの値が変更された時に呼び出されるウォッチャー"""
        self.update(f"現在のカウント: [bold cyan]{new_value}[/bold cyan]")

    def compose(self) -> ComposeResult:
        """子Widgetを配置する"""
        yield Static(f"現在のカウント: {self.count}", id="display")
        yield Horizontal(
            Button("インクリメント (+1)", id="add", variant="success"),
            Button("デクリメント (-1)", id="sub", variant="error"),
            classes="button-bar"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """ボタンが押された時のイベントハンドラ"""
        if event.button.id == "add":
            self.count += 1
        elif event.button.id == "sub":
            self.count -= 1


class CounterApp(App):
    """メインアプリケーションクラス"""
    
    # アプリ全体のキーバインド定義
    BINDINGS = [
        ("q", "quit", "終了"),
        ("r", "reset", "リセット"),
    ]

    # インラインでTCSS（Textual CSS）を記述
    CSS = """
    Screen {
        align: center middle;
        background: $surface;
    }

    CounterWidget {
        width: 60;
        height: auto;
        border: solid green;
        padding: 1 2;
        background: $panel;
    }

    .button-bar {
        margin-top: 1;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        """画面全体のレイアウト"""
        yield Header(show_clock=True)
        yield CounterWidget()
        yield Footer()

    def action_reset(self) -> None:
        """BINDINGSで定義した'reset'アクションの実装"""
        counter = self.query_one(CounterWidget)
        counter.count = 0


if __name__ == "__main__":
    app = CounterApp()
    app.run()
```

### コードの解説
- **`App` と `ComposeResult`**: すべてのTextualアプリは `App` クラスを継承します。`compose()` メソッド内で `yield` を使用してUI要素（Widget）を木構造で組み立てます。
- **リアクティブ変数 (`reactive`)**: `count = reactive(0)` と宣言することで、`self.count += 1` のように値を変更するだけでUIが自動追従します。`watch_count` のような命名規則（`watch_<変数名>`）で変更イベントをキャッチできます。
- **イベントハンドラ**: `on_button_pressed` のように `on_<widget_type>_<event_type>` の命名規則でイベントを受け取ります。
- **BINDINGS**: `("キー", "アクション名", "説明")` のタプルでショートカットを登録できます。`action_<アクション名>` メソッドを定義すると、キー押下時に自動で実行されます。
- **TCSS**: CSSライクな記法でレイアウトや見た目を整えます。`$surface` や `$panel` といった組み込みカラー変数を使うことで、ターミナルのテーマに馴染むデザインが作れます。

---

## 4. 実務で使えるコード例：リアルタイム・システム監視＆ログアナライザー

ここからは、実務でそのまま活用できる応用例として「サーバーのシステムリソース監視 ＆ ログリアルタイム表示ツール」を作成します。

このツールには以下の機能を盛り込みます。
1. **CPU/メモリ使用率のリアルタイム・プログレスバー表示**
2. **プロセス一覧を表示するインタラクティブな `DataTable`**
3. **疑似ログをリアルタイムにストリーミング表示する `RichLog`**
4. **非同期Worker（`Worker` / `set_interval`）を活用したバックグラウンド処理**

### 必要ライブラリの準備
システム情報の取得に `psutil` を使用します。

```bash
pip install psutil
```

### `system_monitor.py`

```python
import asyncio
import random
from datetime import datetime
import psutil

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import Header, Footer, Static, ProgressBar, DataTable, RichLog, Button
from textual.worker import Worker, WorkerState
from textual.reactive import reactive


class ResourceMonitor(Static):
    """CPUとメモリ使用率を表示するWidget"""

    def compose(self) -> ComposeResult:
        yield Static("[bold]CPU 使用率:[/bold]", classes="label")
        yield ProgressBar(total=100, show_percentage=True, id="cpu_bar")
        yield Static("[bold]メモリ 使用率:[/bold]", classes="label")
        yield ProgressBar(total=100, show_percentage=True, id="mem_bar")

    def update_metrics(self, cpu: float, mem: float) -> None:
        """プログレスバーの更新"""
        self.query_one("#cpu_bar", ProgressBar).progress = cpu
        self.query_one("#mem_bar", ProgressBar).progress = mem


class ProcessTable(DataTable):
    """実行中プロセスの一覧を表示するテーブルWidget"""

    def on_mount(self) -> None:
        """Widget配置時の初期設定"""
        self.cursor_type = "row"
        self.add_columns("PID", "プロセス名", "CPU (%)", "メモリ (%)")

    def update_processes() -> None:
        """プロセス情報の更新（外部から呼び出し）"""
        pass  # メインApp側で一括制御


class SystemMonitorApp(App):
    """システム監視ダッシュボード・メインアプリ"""

    TITLE = "OKPy System Monitor & Log Analyzer"
    SUB_TITLE = "Textual Practical Example"

    BINDINGS = [
        ("q", "quit", "終了"),
        ("c", "clear_logs", "ログ消去"),
        ("p", "toggle_pause", "一時停止/再開"),
    ]

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 2;
        grid-rows: 1fr 2fr;
        grid-columns: 1fr 1fr;
        padding: 1;
        grid-gutter: 1;
    }

    #left_top {
        border: round $accent;
        padding: 1;
        background: $panel;
    }

    #right_top {
        border: round $success;
        padding: 1;
        background: $panel;
    }

    #bottom_panel {
        column-span: 2;
        border: round $primary;
        background: $panel;
    }

    .label {
        margin-top: 1;
        margin-bottom: 0;
    }

    ProgressBar {
        width: 100%;
    }

    DataTable {
        height: 100%;
    }

    RichLog {
        height: 100%;
        background: $surface-down;
    }
    """

    is_paused = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        # 左上：リソースプログレスバー
        with Vertical(id="left_top"):
            yield Static("[bold cyan]■ リソース使用状況[/bold cyan]")
            yield ResourceMonitor(id="resource_monitor")

        # 右上：クイックアクションとステータス
        with Vertical(id="right_top"):
            yield Static("[bold green]■ 制御・ステータス[/bold green]")
            yield Static("ステータス: [bold green]監視中[/bold green]", id="status_text")
            yield Horizontal(
                Button("一時停止 / 再開", id="btn_pause", variant="primary"),
                Button("ログクリア", id="btn_clear", variant="warning"),
                classes="label"
            )

        # 下部：プロセス一覧とログビューアを横並び
        with Horizontal(id="bottom_panel"):
            with Vertical(id="table_wrapper"):
                yield Static("[bold yellow]■ 上位プロセス (CPU順)[/bold yellow]")
                yield ProcessTable(id="process_table")
            with Vertical(id="log_wrapper"):
                yield Static("[bold magenta]■ システムログ・ストリーム[/bold magenta]")
                yield RichLog(highlight=True, markup=True, id="sys_log")

        yield Footer()

    def on_mount(self) -> None:
        """アプリ起動時の初期化処理（定期タイマーの設定）"""
        # 1秒ごとにシステムメトリクスを更新
        self.set_interval(1.0, self.refresh_system_data)
        # 1.5秒ごとに疑似ログを出力
        self.set_interval(1.5, self.generate_dummy_log)

    def refresh_system_data(self) -> None:
        """システム情報の取得と画面更新（タイマーコールバック）"""
        if self.is_paused:
            return

        # 1. CPU・メモリの更新
        cpu_percent = psutil.cpu_percent()
        mem_percent = psutil.virtual_memory().percent
        
        res_mon = self.query_one("#resource_monitor", ResourceMonitor)
        res_mon.update_metrics(cpu_percent, mem_percent)

        # 2. プロセス一覧の更新
        table = self.query_one("#process_table", ProcessTable)
        table.clear()

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # CPU使用率順にソートして上位5件を表示
        top_processes = sorted(processes, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:5]

        for p in top_processes:
            table.add_row(
                str(p['pid']),
                p['name'][:15],
                f"{p['cpu_percent']:.1f}",
                f"{p['memory_percent']:.1f}"
            )

    def generate_dummy_log(self) -> None:
        """疑似ログの追記"""
        if self.is_paused:
            return

        log_widget = self.query_one("#sys_log", RichLog)
        now = datetime.now().strftime("%H:%M:%S")

        log_levels = [
            ("[green]INFO[/green]", "データベースへの接続が正常に完了しました。"),
            ("[green]INFO[/green]", "APIリクエストを受信: GET /api/v1/status (200 OK)"),
            ("[yellow]WARN[/yellow]", "メモリ使用量が80%を超過しつつあります。"),
            ("[red]ERROR[/red]", "外部決済APIへの接続タイムアウトが発生しました (再試行中)"),
            ("[green]INFO[/green]", "バックグラウンドクリーンアップジョブが終了しました。")
        ]

        level, msg = random.choice(log_levels)
        log_widget.write(f"[{now}] {level} - {msg}")

    def action_toggle_pause(self) -> None:
        """監視のポーズ／再開切り替え"""
        self.is_paused = not self.is_paused
        status_text = self.query_one("#status_text", Static)
        
        if self.is_paused:
            status_text.update("ステータス: [bold yellow]一時停止中[/bold yellow]")
            self.notify("監視を一時停止しました", severity="warning")
        else:
            status_text.update("ステータス: [bold green]監視中[/bold green]")
            self.notify("監視を再開しました", severity="information")

    def action_clear_logs(self) -> None:
        """ログビューアのクリア"""
        log_widget = self.query_one("#sys_log", RichLog)
        log_widget.clear()
        self.notify("ログを消去しました")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """ボタン押下時の処理"""
        if event.button.id == "btn_pause":
            self.action_toggle_pause()
        elif event.button.id == "btn_clear":
            self.action_clear_logs()


if __name__ == "__main__":
    app = SystemMonitorApp()
    app.run()
```

### この実務コードのポイント

1. **レイアウト制御 (Grid & Flexbox)**:
   - TCSSの `layout: grid;` を利用して画面を2x2のセクションに分割しています。
   - `column-span: 2;` を指定することで、下部のログ／テーブルエリアを横いっぱいに広げています。

2. **非同期タイマー処理 (`self.set_interval`)**:
   - `time.sleep()` を使ってしまうとUI全体がフリーズします。Textualでは `self.set_interval(秒数, コールバック関数)` を使用することで、イベントループを止めずに定期処理を実行できます。

3. **`DataTable` の活用**:
   - `clear()` と `add_row()` を組み合わせることで、リアルタイムに変化するプロセス一覧を滑らかに書き換えています。

4. **`RichLog` とリッチテキスト**:
   - Richのマークアップ記法（`[green]...[/green]` や `[bold]...[/bold]`）を直接流し込める `RichLog` を使用することで、視認性の高いログビューアを実現しています。

5. **デスクトップ風通知 (`self.notify`)**:
   - `self.notify()` メソッドを呼ぶだけで、ターミナルの右上／右下にトースト通知をオーバーレイ表示できます。

---

## 5. 実務開発での注意点・ハマりポイント

Textualを使ってツールを開発する際、初心者が陥りがちなポイントと解決策をまとめました。

### ① ブロッキング処理によるUIフリーズ
**問題:** 外部API通信、重いファイルI/O、巨大な計算などを同期処理で実行すると、画面の描画やキー入力の応答が止まります。

**対策:** 
Textualの **Worker（ワーカー）機能** や `asyncio` を活用します。`@work` デコレータを付与することで、重い処理をバックグラウンドスレッド/タスクで安全に実行できます。

```python
from textual.worker import work

class MyApp(App):
    @work(exclusive=True, thread=True)
    def fetch_heavy_data(self) -> dict:
        # 重い同期処理（例: requestsを使った通信や巨大ファイルの読み込み）
        import requests
        response = requests.get("https://api.example.com/large-data")
        return response.json()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        # バックグラウンド処理を開始（UIはブロックされない）
        self.fetch_heavy_data()
```

### ② TCSSと標準Web CSSの違い
**問題:** WebのCSSと同じ感覚でプロパティを指定しても効かない場合があります。

**対策:**
- Textual CSSはWeb CSSの一部仕様を踏襲した**独自ダイアレクト**です。
- サポートされている主要なプロパティ: `width`, `height`, `margin`, `padding`, `background`, `color`, `border`, `layout` (`grid` / `vertical` / `horizontal`), `align` など。
- 変数は `$accent`, `$primary`, `$success`, `$error` などの組み込みパレットや、自作のカラーコード (`#ff0055`) を利用できます。

### ③ ターミナルエミュレータのカラー・フォント互換性
**問題:** 開発環境では綺麗に見えていたUIが、サーバー環境（標準のWindows CMDや古いLinux端末）に持って行くと表示が崩れたり色が正しく出ない。

**対策:**
- TrueColor（24bitカラー）および UTF-8/Unicode フォントがサポートされているターミナル（Windows Terminal, iTerm2, Alacritty, Kitty, VS Code統合ターミナル等）での利用を推奨します。
- 演出として特殊な絵文字やUnicode記号（`■` や `✔` など）を多用する場合は、表示崩れを防ぐためにフォント設定にも注意を払う必要があります。

---

## 6. FAQ（よくある質問）

### Q1. `Rich` と `Textual` の使い分けはどうすれば良いですか？
**A.** 
- **Rich**: 「ワンショットのコマンド出力」の装飾に適しています。例えば CLI ツールの実行結果として綺麗なテーブルやプログレスバーを1回出力して終了するような用途（`rich.print()`）です。
- **Textual**: 「画面全体を占有するインタラクティブなアプリ」に適しています。キーボード操作やマウスイベントを受け取り、画面の一部を部分更新し続けるツール（ダッシュボード、TUIエディタ、ファイルマネージャー等）を作成する場合はTextualを選択します。

### Q2. 開発したTextualアプリをWebブラウザ上で動作させることは可能ですか？
**A.** 
**はい、可能です。** Textual開発チームは `textual-web` というツールを提供しています。これを使用すると、ターミナル用に書いたTextualコードを一行も変更することなく、Webブラウザ経由で操作可能なWebアプリとして公開・サーブすることができます。社内ツールをCLI/Webの両方で共有したい場合に極めて有効です。

```bash
pip install textual-web
textual-web --config config.toml
```

### Q3. アプリケーションのユニットテストやUIテストはどのように行いますか？
**A.** 
Textualには強力なテスト用 harness（Pilot API）が標準で組み込まれています。`pytest` と組み合わせて、画面の起動、ボタンのクリック、キー入力、および表示テキストの検証を headless（画面非表示）環境でテスト可能です。

```python
import pytest
from my_app import CounterApp

@pytest.mark.asyncio
async def test_counter_app():
    app = CounterApp()
    # run_test()でパイロットモードを起動
    async with app.run_test() as pilot:
        # ボタン押下をシミュレート
        await pilot.click("#add")
        # リアクティブ変数の検証
        counter = app.query_one("CounterWidget")
        assert counter.count == 1
```

---

## まとめ

Textualの登場により、PythonでのTUI開発は「泥臭いターミナル制御コードを書く作業」から「モダンなWeb/GUIアプリ開発と同等の洗練された体験」へと進化しました。

社内用の運用・監視ツールや、CLIツールのリッチ化を検討している方は、ぜひTextualを活用して快適で美しいターミナルアプリケーションを構築してみてください！
