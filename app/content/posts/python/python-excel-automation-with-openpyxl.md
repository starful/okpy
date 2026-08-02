---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250909185612.png
date: 2025-10-20
hatena_path: /entry/2025/10/20/104658
slug: python-excel-automation-with-openpyxl
summary: "皆さん、こんにちは！Pythonの魔法使いを目指す皆さん、そして日々データと格闘するエンジニアの皆さん、お元気ですか？\U0001F60E 今日は、皆さんのExcel作業を劇的にラクにしてくれる、とっておきのPythonライブラリをご紹介します！その名も「OpenPyXL」！"
title: Python Excel Automation with OpenPyXL
---

# Python Excel Automation with OpenPyXL

# Python OpenPyXL: まだExcel作業を手作業で消耗していますか？🐍✨

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250909185612.png)

皆さん、こんにちは！Pythonの魔法使いを目指す皆さん、そして日々データと格闘するエンジニアの皆さん、お元気ですか？😎 今日は、皆さんのExcel作業を劇的にラクにしてくれる、とっておきのPythonライブラリをご紹介します！その名も「**OpenPyXL**」！

「え、PythonでExcelを操作できるの？」「マクロとかVBAって難しそう…」なんて思っているそこのあなた！大丈夫です、OpenPyXLはPythonのコードを書くだけで、まるで魔法のようにExcelファイルを自由に操れるようになる、まさに夢のようなツールなんです。手作業でのコピペや、退屈なデータ入力作業にさよならを告げましょう！👋

このブログ記事では、Pythonを始めたばかりの初心者の方でも、OpenPyXLを使ってExcelファイルを読み書き・編集する方法を、とっても分かりやすく解説していきます。さあ、一緒にPythonとOpenPyXLの素晴らしい世界へ飛び込みましょう！🚀

📝 **TL;DR (3行要約)**
*   **OpenPyXL**は、PythonでExcelファイル（.xlsx形式）を読み書き・編集できるライブラリです。
*   手作業でのデータ入力、レポート作成、データ抽出など、面倒なExcel作業を自動化したい時に大活躍！
*   シンプルで直感的なAPI（操作方法）なので、Python初心者でも比較的簡単に使いこなせるのが最大の魅力です。

---

### 1. 🤔 OpenPyXLとは何か？

OpenPyXLは一言で言うと、「**PythonからExcelファイルを扱うための強力なパートナー**」です！💼

皆さんが普段使っているExcelファイルを、Pythonプログラムの中からまるで自分の手足のように操れるようにしてくれるライブラリなんです。

ちょっと想像してみてください。あなたは今、たくさんのExcelファイルから特定のデータを抜き出して集計したり、毎週同じフォーマットのレポートを作成したりする作業を任されています。手作業でやると、時間がかかるし、ミスも発生しやすいですよね。

ここでOpenPyXLの登場です！OpenPyXLは、まるで**あなた専用の敏腕秘書**のように、Pythonの指示に従ってExcelファイルを開き、セルにデータを入力したり、既存のデータを読み取ったり、新しいシートを追加したり、グラフを作成したり…と、ありとあらゆるExcel操作を自動でこなしてくれるんです。

この秘書は、疲れることもなく、文句も言わず、言われた通りに正確に作業を進めてくれます。まさに、退屈で時間のかかるExcel作業から私たちを解放してくれる、頼もしい存在だと思いませんか？😊

---

### 2. 🚀 いつ使用するの？ (主要使用事例)

OpenPyXLは、特に以下のような場面でその真価を発揮します。あなたの日常業務にも役立つヒントがあるかもしれませんよ！💡

1.  **📊 定期的なレポート自動生成**
    *   毎日の売上データや、毎週の進捗状況などをExcelでレポートとしてまとめる作業、ありますよね？OpenPyXLを使えば、データベースから最新のデータを取得し、それを元に事前に用意したテンプレートのExcelファイルに自動でデータを入力し、グラフまで生成して保存する、といった一連の作業を自動化できます。もう締め切りギリギリで焦る必要はありません！😉

2.  **🔍 大量のExcelファイルから特定のデータ抽出・集計**
    *   「100個のExcelファイルの中から、特定のキーワードが含まれる行だけを抜き出して、別のシートにまとめたい」なんていう、気が遠くなるような作業に直面したことはありませんか？OpenPyXLは、複数のExcelファイルを次々に開き、必要な情報だけを抽出・加工して、新しいExcelファイルに集約する、といった処理をあっという間に実行してくれます。まさにデータ分析の強い味方！💪

3.  **📝 データ入力・編集の自動化**
    *   何かのシステムから出力されたCSVファイルやテキストファイルを、Excelの特定のフォーマットに合わせて整形して入力し直す、といった作業もOpenPyXLの得意分野です。例えば、新しい顧客リストがテキストファイルで届いたとして、それを既存の顧客管理Excelファイルの決められた列に自動で追加していく、なんてことも可能です。手作業での入力ミスも激減しますよ！✨

---

### 3. 💻 インストール方法

さて、この素晴らしいOpenPyXLを使い始めるのはとっても簡単です！Pythonのライブラリは、`pip`というツールを使ってインストールするのが一般的です。

あなたのターミナル（WindowsならコマンドプロンプトやPowerShell、Mac/Linuxならターミナル）を開いて、以下のコマンドを打ち込むだけ！🚀

```bash
pip install openpyxl
```

このコマンドを実行すると、OpenPyXLがあなたのPython環境に導入され、すぐに使えるようになります。もし、Pythonを複数インストールしている場合は、特定のPython環境にインストールするために `python -m pip install openpyxl` のように実行することもありますよ。

インストールが完了したら、Pythonのスクリプトで `import openpyxl` と書いてエラーが出なければ成功です！おめでとうございます！🎉

---

### 4. 🛠️ 実際動するサンプルコード

それでは、実際にOpenPyXLを使って簡単なExcelファイルを読み書きするコードを見てみましょう！今回は、「新しいExcelファイルを作成し、データを書き込み、保存する」そして「既存のExcelファイルを読み込み、特定のセルデータを表示する」という一連の操作を行います。

このコードをコピーして、あなたのPCでぜひ実行してみてください！🤩

```python
import openpyxl
from openpyxl.utils import get_column_letter

# --- 1. 新しいExcelファイルを作成し、データを書き込む ---

# 新しいワークブック（Excelファイル全体）を作成
workbook = openpyxl.Workbook()

# アクティブな（現在選択されている）ワークシートを取得
# デフォルトでは 'Sheet' という名前のシートが一つ作成されます
sheet = workbook.active
sheet.title = "商品リスト" # シートの名前を変更

# ヘッダー行を書き込む
sheet['A1'] = "商品ID"
sheet['B1'] = "商品名"
sheet['C1'] = "価格"
sheet['D1'] = "在庫数"

# データを書き込む
data = [
    (101, "ノートPC", 120000, 50),
    (102, "ワイヤレスマウス", 3500, 150),
    (103, "メカニカルキーボード", 15000, 80),
    (104, "Webカメラ", 7000, 100),
]

# forループを使ってデータをシートに追加
for row_data in data:
    sheet.append(row_data)

# セルのスタイルを設定してみよう (例: B列の幅を広げる)
sheet.column_dimensions['B'].width = 20

# 特定のセルにコメントを追加してみよう
cell = sheet['A1']
cell.comment = openpyxl.comments.Comment("これは商品IDです", "Python User")

# 作成したExcelファイルを保存
file_name = "my_products.xlsx"
workbook.save(file_name)
print(f"'{file_name}' を作成し、データを保存しました。")

# --- 2. 作成したExcelファイルを読み込み、データを表示する ---

print(f"\n--- '{file_name}' を読み込みます ---")

# 既存のワークブックを読み込む
loaded_workbook = openpyxl.load_workbook(file_name)

# シート名を確認
print(f"ワークブック内のシート: {loaded_workbook.sheetnames}")

# '商品リスト'という名前のシートを取得
loaded_sheet = loaded_workbook["商品リスト"]

print(f"シート '{loaded_sheet.title}' のデータ:")

# 特定のセルからデータを読み取る
print(f"A1セルの値: {loaded_sheet['A1'].value}")
print(f"B2セルの値: {loaded_sheet['B2'].value}") # ノートPC

# 行ごとにデータを読み取る (ヘッダー含む)
for row in loaded_sheet.iter_rows(min_row=1, max_col=4, values_only=True):
    print(row)

# 特定の列からデータを読み取る (例: 商品名だけを抜き出す)
print("\n--- 商品名リスト ---")
for row_index in range(2, loaded_sheet.max_row + 1): # 2行目から最終行まで
    product_name = loaded_sheet.cell(row=row_index, column=2).value
    print(product_name)

# ワークブックを閉じる (明示的に閉じる必要はないが、推奨される場合もある)
loaded_workbook.close()

print("\n--- 処理が完了しました！ ---")
```

---

### 5. 🔍 コード詳細説明

上記のサンプルコードがどのように動作しているのか、一行ずつ、あるいはブロックごとに詳しく見ていきましょう！初心者の方でも「なるほど！」と膝を打つように解説します。🙌

```python
import openpyxl
from openpyxl.utils import get_column_letter
```
*   `import openpyxl`: これがOpenPyXLライブラリを使うための宣言です。Pythonプログラムの冒頭でいつも書くおまじないのようなものですね。
*   `from openpyxl.utils import get_column_letter`: これは、`openpyxl.utils`モジュールの中から`get_column_letter`という特定の関数だけをインポートしています。セルの列を数値からアルファベット（例: 1 -> A, 2 -> B）に変換するのに便利な関数ですが、今回のサンプルでは直接使っていません。しかし、より複雑なExcel操作では役立つことがあります。

```python
# --- 1. 新しいExcelファイルを作成し、データを書き込む ---

workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "商品リスト" # シートの名前を変更
```
*   `workbook = openpyxl.Workbook()`: 新しいExcelファイル（専門用語で「ワークブック」と呼びます）をメモリ上に作成します。まだファイルとしては保存されていません。
*   `sheet = workbook.active`: 作成したワークブックには、デフォルトで「Sheet」という名前のシートが一つだけあります。`workbook.active`はそのアクティブな（現在選択されている）シートを取得する方法です。
*   `sheet.title = "商品リスト"`: この行で、デフォルトのシート名を「商品リスト」に変更しています。こうすることで、より分かりやすいExcelファイルになりますね。

```python
# ヘッダー行を書き込む
sheet['A1'] = "商品ID"
sheet['B1'] = "商品名"
sheet['C1'] = "価格"
sheet['D1'] = "在庫数"
```
*   `sheet['A1'] = "商品ID"`: これは、シートの特定のセルに値を書き込む最も基本的な方法です。Excelでセル番地を指定するのと同じように、`['A1']`と書くだけでそのセルにアクセスし、`=`を使って値を代入できます。とっても直感的ですね！

```python
# データを書き込む
data = [
    (101, "ノートPC", 120000, 50),
    (102, "ワイヤレスマウス", 3500, 150),
    (103, "メカニカルキーボード", 15000, 80),
    (104, "Webカメラ", 7000, 100),
]

for row_data in data:
    sheet.append(row_data)
```
*   `data = [...]`: Excelに書き込みたいデータをPythonのリスト形式で準備しています。各タプル`()`がExcelの一行に対応します。
*   `for row_data in data: sheet.append(row_data)`: この`append()`メソッドが超便利！リストやタプル形式のデータを渡すと、シートの**一番下の空いている行**に自動で一行追加してくれます。データを順番に追加していくときに非常に役立ちます。

```python
# セルのスタイルを設定してみよう (例: B列の幅を広げる)
sheet.column_dimensions['B'].width = 20

# 特定のセルにコメントを追加してみよう
cell = sheet['A1']
cell.comment = openpyxl.comments.Comment("これは商品IDです", "Python User")
```
*   `sheet.column_dimensions['B'].width = 20`: セルのスタイル（書式）を調整する例です。ここではB列の幅を`20`に設定しています。OpenPyXLでは、列の幅や行の高さ、フォント、背景色など、さまざまなスタイルをプログラムで変更できます。
*   `cell.comment = openpyxl.comments.Comment(...)`: Excelのセルにコメントを追加しています。`openpyxl.comments.Comment`を使ってコメントオブジェクトを作成し、それをセルの`comment`プロパティに代入するだけです。

```python
# 作成したExcelファイルを保存
file_name = "my_products.xlsx"
workbook.save(file_name)
print(f"'{file_name}' を作成し、データを保存しました。")
```
*   `workbook.save(file_name)`: これが最も重要な部分！メモリ上に作成したワークブックを、指定したファイル名（`my_products.xlsx`）でPCに実際にExcelファイルとして保存します。この行を実行するまで、ファイルは作成されません。

---

```python
# --- 2. 作成したExcelファイルを読み込み、データを表示する ---

print(f"\n--- '{file_name}' を読み込みます ---")

loaded_workbook = openpyxl.load_workbook(file_name)
```
*   `loaded_workbook = openpyxl.load_workbook(file_name)`: 既存のExcelファイル（ここでは先ほど保存した`my_products.xlsx`）を読み込んで、Pythonのワークブックオブジェクトとして扱えるようにします。

```python
print(f"ワークブック内のシート: {loaded_workbook.sheetnames}")
loaded_sheet = loaded_workbook["商品リスト"]
```
*   `loaded_workbook.sheetnames`: ワークブック内に存在するすべてのシートの名前をリストとして取得できます。
*   `loaded_sheet = loaded_workbook["商品リスト"]`: 読み込んだワークブックの中から、名前を指定して特定のシートを取得しています。

```python
print(f"A1セルの値: {loaded_sheet['A1'].value}")
print(f"B2セルの値: {loaded_sheet['B2'].value}") # ノートPC
```
*   `loaded_sheet['A1'].value`: 読み込んだシートから、特定のセル（A1）の**値**を取得しています。`.value`を付けないと、セルオブジェクト自体が取得されるので注意してください。

```python
# 行ごとにデータを読み取る (ヘッダー含む)
for row in loaded_sheet.iter_rows(min_row=1, max_col=4, values_only=True):
    print(row)
```
*   `loaded_sheet.iter_rows(...)`: これはシートのデータを効率的に読み込むためのメソッドです。
    *   `min_row=1`: 1行目から読み込みを開始します。
    *   `max_col=4`: 4列目（D列）まで読み込みます。
    *   `values_only=True`: これが重要！各セルオブジェクトではなく、セルの値（value）だけをタプル形式で取得してくれます。もし`False`（または指定しない）場合、各要素はセルオブジェクトになります。

```python
# 特定の列からデータを読み取る (例: 商品名だけを抜き出す)
print("\n--- 商品名リスト ---")
for row_index in range(2, loaded_sheet.max_row + 1): # 2行目から最終行まで
    product_name = loaded_sheet.cell(row=row_index, column=2).value
    print(product_name)
```
*   `loaded_sheet.max_row`: シートのデータが存在する最終行の番号を取得します。これを使えば、データが何行目まであるかをいちいち数える必要がありません。
*   `loaded_sheet.cell(row=row_index, column=2).value`: `sheet['B2']`のようにセル番地で指定する代わりに、`cell()`メソッドを使って行番号と列番号（数字）でセルを指定することもできます。`column=2`はB列を意味します。ループ処理で動的にセルを指定したいときに非常に便利です。

```python
loaded_workbook.close()
```
*   `loaded_workbook.close()`: 読み込んだワークブックを閉じます。通常、Pythonスクリプトの終了時に自動的に閉じられますが、明示的に閉じることでメモリを解放し、ファイルがロックされるのを防ぐことができます。特に大きなファイルを扱う場合や、ループ内で多くのファイルを操作する場合には意識しておくと良いでしょう。

これでOpenPyXLの基本的な使い方はバッチリです！💪 コードを読み解いていくと、Pythonの強力さとOpenPyXLの便利さがじんわりと伝わってくるはずです。

---

### ⚠️ 注意する点または꿀팁

OpenPyXLを使いこなす上で、Python初心者の方がつまづきやすい点や、知っておくと便利な「꿀팁（クルティプ＝韓国語で"裏技"や"秘訣"）」をいくつかご紹介します！✨

1.  **💾 `workbook.save()`を忘れずに！**
    *   OpenPyXLでシートにデータを書き込んだり、書式を変更したりしても、`workbook.save("ファイル名.xlsx")`を実行するまで、**変更はファイルに反映されません！** メモリ上での作業なので、保存し忘れると全ての作業が無駄になってしまいます。これは本当に基本的なことですが、ついつい忘れがちなので、作業の区切りごとに保存する癖をつけるようにしましょう。特に既存ファイルを更新する場合は、元のファイルを上書きしないようにバックアップを取っておくのが賢明です。

2.  **🔒 既存のExcelファイルを開く際の注意 (読み書きモード)**
    *   `openpyxl.load_workbook('ファイル名.xlsx')` でファイルを開くとき、デフォルトでは読み書き（read/write）モードで開かれます。もし、**ファイルを開いている間にPythonスクリプトがクラッシュしたり、適切に閉じられなかったりすると、ファイルが破損する可能性があります**。
    *   読み取り専用で開く場合は、`openpyxl.load_workbook('ファイル名.xlsx', read_only=True)` と`read_only=True`を指定することで、より安全にファイルにアクセスできます。特に大きなファイルを扱う場合や、変更の必要がない場合は、このオプションを使うのがおすすめです。

3.  **🌟 Pythonのリスト操作スキルが鍵！**
    *   OpenPyXLを使ってExcelを効率的に操作するには、Pythonのリストや辞書、タプルといったデータ構造を使いこなすスキルが非常に重要になります。Excelのデータを行や列のリストとして扱い、Pythonの強力なデータ処理能力で加工してからOpenPyXLで書き戻す、という流れが一般的です。ぜひPythonのリスト内包表記や辞書の操作方法などを復習してみてくださいね。これらをマスターすれば、より複雑なExcel操作も楽々こなせるようになりますよ！

---

### 🔗 一緒に보면 좋은 라이브러리 (一緒に見ると良いライブラリ)

OpenPyXLだけでもExcel操作は十分にできますが、他のライブラリと組み合わせることで、さらに強力なデータ処理が可能になります！ここで一つ、Pythonでデータ分析をするなら絶対に知っておきたいライブラリをご紹介します。

**🐼 Pandas (パンダス)**

*   **役割**: Pandasは、Pythonでデータ分析を行うためのデファクトスタンダード（事実上の標準）ライブラリです。特に「データフレーム（DataFrame）」という表形式のデータ構造が強力で、Excelのシートやデータベースのテーブルのようなデータを非常に効率的に扱えます。
*   **OpenPyXLとの連携**: OpenPyXLがExcelファイル自体を直接操作するのに対し、PandasはExcelファイルからデータを読み込み、メモリ上で強力なデータ処理（フィルタリング、集計、結合、整形など）を行った後、その結果を新しいExcelファイルとしてOpenPyXLを使って書き出す、という連携がよく行われます。
    *   例えば、`pandas.read_excel()`でExcelファイルを読み込み、PandasのDataFrameでゴリゴリとデータを加工し、最後に`DataFrame.to_excel()`でOpenPyXLの機能を使って新しいExcelファイルとして保存する、といった流れです。
*   **こんな時に便利**: 大量のデータ分析、複雑なデータ変換、統計処理、他のデータソース（CSV, データベースなど）との連携が必要な場合。

OpenPyXLでExcelの入出力の基本をマスターしたら、次はぜひPandasの世界に足を踏み入れてみてください。Pythonでのデータ操作の可能性がぐっと広がりますよ！✨

---

### 6. 🎉 마무리

皆さん、今日はOpenPyXLという素晴らしいPythonライブラリについて、じっくりと見てきました。Pythonを使ってExcelファイルを自動で操作する方法、そしてその便利さを少しでも感じていただけたでしょうか？😊

手作業でのExcel作業は、時間もかかるし、ミスも発生しやすいですよね。しかし、OpenPyXLを使えば、そういった退屈で繰り返し行う作業をPythonのコードに任せて、皆さんはもっと創造的で価値のある仕事に集中できるようになります。これは、まさにプログラミングの醍醐味の一つです！

Python学習の旅は、時に難しいと感じることもあるかもしれません。しかし、OpenPyXLのように、皆さんの日々の業務や学習に直接役立つツールがあることを知れば、きっとモチベーションもアップするはずです。

さあ、今日学んだ知識を活かして、ぜひご自身のPCでサンプルコードを動かしてみてください。そして、もっと「こんなことができたらいいな」というアイデアがあれば、OpenPyXLの公式ドキュメントや、インターネット上の豊富な情報を調べて、実際に挑戦してみてください。きっと新しい発見があるはずです！

**🔥 あなたへの挑戦課題！**
今回のサンプルコードを少しだけ修正して、以下のことにチャレンジしてみましょう！

1.  **既存のデータに新しい商品を追加してみる**
    *   `my_products.xlsx`を読み込んだ後、別の商品データ（例: `(105, "USBハブ", 2500, 200)`）を`append()`メソッドを使ってシートに追加し、別のファイル名（例: `my_updated_products.xlsx`）で保存してみてください。
2.  **特定の商品の価格を変更してみる**
    *   例えば、「ノートPC」の価格を120000から115000に変更し、ファイルを上書き保存してみましょう。ヒント：`loaded_sheet.cell(row=行番号, column=列番号).value = 新しい値`を使ってください。

これらの挑戦を通じて、OpenPyXLの使い方がさらに身につくはずです。あなたのPythonスキルがグングン成長していくことを応援しています！Go, Pythonistas!🚀💖