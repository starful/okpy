---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20251210210547.png
date: 2025-12-31
hatena_path: /entry/2025/12/31/090000_1
slug: pythonで画像認識-まだゼロからコードを書いて消耗してる-pytorch-visionで世界が変わる話
summary: PyTorch Visionは、PyTorchで画像認識AIを開発するための超便利な公式ツールキットです。
title: Pythonで画像認識、まだゼロからコードを書いて消耗してる？PyTorch Visionで世界が変わる話
---

# Pythonで画像認識、まだゼロからコードを書いて消耗してる？PyTorch Visionで世界が変わる話

![image](https://storage.googleapis.com/ok-project-assets/okpy/20251210210547.png)

📝 **TL;DR (3行要約)**

PyTorch Visionは、PyTorchで画像認識AIを開発するための超便利な公式ツールキットです。
有名なデータセットや強力な学習済みモデルが揃っており、面倒な準備の手間を大幅に削減できます。
画像分類や物体検出といった高度なタスクを、驚くほど短いコードで手軽に試したい時に絶大な威力を発揮します。

***

### 1. 🤔 一体PyTorch Visionとは何？（核心的な役割と主な使用例）

PythonでAI、特に「画像認識」を学ぼうとすると、たくさんの専門用語や複雑な理論が出てきて、心が折れそうになった経験はありませんか？「ディープラーニングモデルを構築する」「大規模なデータセットを用意する」「画像を適切に前処理する」…これらをすべてゼロからやろうとすると、膨大な時間と知識が必要になります。

そんな初心者の前に立ちはだかる高い壁を、一気に乗り越えるための魔法の杖、それが **PyTorch Vision** です。

- **核心的な役割 🍳: AI開発における「高級料理キット」**

PyTorch Visionの役割を例えるなら、それは**「AI開発のための高級料理キット」**です。

あなたが「画像から猫を認識するAI」という絶品料理を作りたいとしましょう。普通に料理をするなら、まずレシピを探し（モデルの構造を設計し）、世界中の市場を巡って最高の食材を集め（大規模な画像データセットを収集・整理し）、野菜の皮をむいたり、肉の下味をつけたりする下ごしらえ（画像のリサイズや正規化）をしなければなりません。これは非常に手間がかかりますよね。

PyTorch Visionは、この面倒なプロセスをすべて肩代わりしてくれます。
*   **世界トップクラスのシェフが考案したレシピ（学習済みモデル）**
*   **最高品質の厳選された食材（有名なデータセット）**
*   **下ごしらえ済みのカット野菜（便利な画像変換ツール）**

これらがすべて一つのパッケージになっているのです。あなた（開発者）は、このキットを使って、最後の味付けを少し変えたり（転移学習）、盛り付けを工夫したり（推論結果の表示）するだけで、プロ顔負けの料理をあっという間に完成させることができます。

つまり、PyTorch Visionは**「画像認識AI開発における面倒で時間のかかる部分をパッケージ化し、開発者が本当に集中したい創造的な部分に時間を使えるようにしてくれる」**ライブラリなのです。

- **主な使用例 🖼️: こんな時に真価を発揮する！**

では、具体的にどんな料理（タスク）が得意なのでしょうか？代表的な例を3つ見ていきましょう。

1.  **画像分類 (Image Classification)**
    これは最も基本的で代表的なタスクです。「この画像に写っているのは、猫ですか？犬ですか？それとも車ですか？」のように、画像全体が何であるかを一つのラベルで分類します。
    PyTorch Visionには、`ResNet`, `VGG`, `MobileNet` といった、画像分類コンテストで名を馳せた伝説的なモデルたちが、すでに学習済みの状態で収録されています。これらを使えば、あなたが用意した一枚の画像を、数行のコードで「これは98%の確率でゴールデンレトリバーです」と予測させることが可能です。Webサービスの画像フィルタリングや、スマートフォンの写真アプリでの自動タグ付けなどに活用されています。

2.  **物体検出 (Object Detection)**
    画像分類から一歩進んで、「画像の中のどこに、何が写っているか」を四角い枠（バウンディングボックス）で囲って特定するタスクです。例えば、交通量の調査で「この画像には車が3台、人が2人写っていて、それぞれの位置はここです」とAIに答えさせることができます。
    PyTorch Visionは `Faster R-CNN` や `SSD` といった強力な物体検出モデルを提供しており、自動運転技術における歩行者や障害物の検知、防犯カメラ映像からの不審者検知、工場の生産ラインでの不良品検出など、より高度で実用的なアプリケーションの基礎となります。

3.  **転移学習 (Transfer Learning)**
    これがPyTorch Visionの真骨頂であり、多くの開発者がこのライブラリを愛用する最大の理由です。転移学習とは、**「あるタスクで賢くなったモデルの知識を、別の新しいタスクに流用する」**技術のことです。
    例えば、PyTorch Visionに入っているモデルは、何百万枚もの一般的な画像（犬、猫、車、飛行機など1000種類）を見て学習しています。この「物体の形や色、質感を見分ける基本的な視力」は、他のタスクにも応用できます。
    あなたが「花の種類を分類するAI」や「自社製品の傷を検出するAI」を作りたいとします。そのために何百万枚もの画像を集めるのは現実的ではありません。しかし、転移学習を使えば、数百〜数千枚程度の独自の画像データを用意するだけで、既存の学習済みモデルを「再教育」し、非常に高い精度を持つ専用AIを短時間で作り上げることができるのです。これは、AI開発のコストと時間を劇的に削減する、革命的なアプローチです。

このように、PyTorch Visionは、AI開発の第一歩を踏み出すための強力なサポーターであり、同時にプロフェッショナルな開発を加速させるためのパワフルなツールでもあるのです。

***

### 2. 💻 インストール方法

PyTorch Visionは、AIの計算を担当する本体である `torch` と一緒にインストールするのが一般的です。ターミナル（またはコマンドプロンプト）で以下のコマンドを実行するだけで、必要なものがすべて揃います。

```bash
pip install torch torchvision
```

もし、画像ファイルを扱う際にURLからダウンロードしたり、ファイルを開いたりする処理も行いたい場合は、`requests` と `Pillow` もインストールしておくと便利です。今回のサンプルコードでも使用します。

```bash
pip install requests Pillow
```

これで準備は完了です！

***

### 3. 🛠️ 実際に動作するサンプルコード

百聞は一見に如かず。PyTorch Visionの力を体感してみましょう。
以下のコードは、世界的に有名な画像認識モデル「ResNet-50」を使って、Web上にある犬の画像をAIが何だと認識するかを予測する、完全なサンプルです。このコードをコピーして、`classify_image.py` のような名前で保存し、実行してみてください。

```python
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import requests
import json
from io import BytesIO

# ----------------------------------------------------------------
# 1. AIモデルの召喚：学習済みモデルのロード
# ----------------------------------------------------------------
print("🤖 学習済みモデルをダウンロードしています...")
# ImageNetで事前学習済みのResNet-50モデルをロード
# `weights`に`DEFAULT`を指定すると、現在推奨されている最新の重みを自動で取得してくれます。
weights = models.ResNet50_Weights.DEFAULT
model = models.resnet50(weights=weights)

# モデルを推論モードに設定（これが重要！）
model.eval()
print("✅ モデルの準備が完了しました。")

# ----------------------------------------------------------------
# 2. 画像の準備：URLからの読み込みと前処理
# ----------------------------------------------------------------
# 予測したい画像のURL
# ここを好きな画像のURLに変えて試してみてください！
# 例：猫 -> https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg
# 例：車 -> https://www.hdcarwallpapers.com/walls/porsche_911_carrera_s_2019_4k-HD.jpg
IMAGE_URL = "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg"

print(f"🖼️ 画像をダウンロードしています: {IMAGE_URL}")
try:
    response = requests.get(IMAGE_URL)
    response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
    img = Image.open(BytesIO(response.content))
except requests.exceptions.RequestException as e:
    print(f"エラー: 画像のダウンロードに失敗しました。 {e}")
    exit()

# モデルに入力するために画像を変換する前処理パイプラインを定義
# この前処理は、モデルが学習された時と全く同じ方法で行う必要があります。
# `weights.transforms()`を使えば、そのモデルに最適な前処理を自動で取得できます。
preprocess = weights.transforms()

# 画像に前処理を適用
# `unsqueeze(0)`は、バッチ次元を追加するためのおまじないです（AIモデルは通常、複数の画像をまとめて処理するため）。
input_tensor = preprocess(img)
input_batch = input_tensor.unsqueeze(0) 
print("✅ 画像の前処理が完了しました。")

# ----------------------------------------------------------------
# 3. 推論の実行：AIによる予測
# ----------------------------------------------------------------
print("🧠 AIが画像を分析しています...")
# 勾配計算を無効にして、メモリ消費を抑え、計算を高速化します
with torch.no_grad():
    output = model(input_batch)
print("✅ 予測が完了しました。")

# ----------------------------------------------------------------
# 4. 結果の解釈：人間がわかる言葉へ翻訳
# ----------------------------------------------------------------
# モデルの出力（logit）を確率に変換
probabilities = torch.nn.functional.softmax(output[0], dim=0)

# ImageNetの1000クラスのラベル情報を取得
# 初回実行時にラベルファイルがダウンロードされます
LABELS_URL = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
labels_response = requests.get(LABELS_URL)
labels = json.loads(labels_response.text)

# 最も確率の高いトップ5の予測を取得
top5_prob, top5_catid = torch.topk(probabilities, 5)

print("\n--- 予測結果 ---")
for i in range(top5_prob.size(0)):
    category_index = top5_catid[i].item()
    category_name = labels[category_index]
    probability = top5_prob[i].item()
    print(f"{i+1}. {category_name}: {probability*100:.2f}%")

```

実行すると、ターミナルに以下のような結果が表示されるはずです。（初回実行時はモデルの重みデータやラベルファイルのダウンロードに少し時間がかかります）

```
🤖 学習済みモデルをダウンロードしています...
✅ モデルの準備が完了しました。
🖼️ 画像をダウンロードしています: https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg
✅ 画像の前処理が完了しました。
🧠 AIが画像を分析しています...
✅ 予測が完了しました。

--- 予測結果 ---
1. Samoyed: 70.32%
2. Pomeranian: 6.22%
3. great Pyrenees: 5.86%
4. Eskimo dog: 3.55%
5. keeshond: 3.33%
```
すごいでしょう？AIは提供された画像を70%以上の確率で「サモエド」という犬種だと正しく認識しました！

***

### 4. 🔍 コードの詳細説明

さて、魔法のように動いたコードですが、一体中で何が行われているのでしょうか？初心者がつまずかないように、各ブロックの役割を解説していきます。

- **チャンク1: AIモデルの召喚 🤖**
  ```python
  weights = models.ResNet50_Weights.DEFAULT
  model = models.resnet50(weights=weights)
  model.eval()
  ```
  ここはAIモデルを準備している部分です。
  *   `models.ResNet50_Weights.DEFAULT`: 「ResNet-50というモデルの、現在最も推奨されている学習済みバージョン（重み）を使います」という宣言です。PyTorch Visionの便利な機能で、これにより最高の性能を持つモデルを簡単に指定できます。
  *   `models.resnet50(weights=weights)`: 指定された重みを使って、ResNet-50モデルのインスタンスを作成します。この一行だけで、複雑なニューラルネットワークの構造がメモリ上に構築され、学習済みの知識（重み）がセットされます。
  *   `model.eval()`: これは非常に重要な一行です。「これからこのモデルを『評価（推論）モード』で使います」というスイッチをONにする命令です。AIモデルは学習時と推論時で、内部の動きが少し変わる部分（例えばDropout層やBatchNorm層）があります。このスイッチを切り替えないと、意図しない予測結果になる可能性があるため、推論する際には必ず呼び出すお作法だと覚えておきましょう。

- **チャンク2: 画像の準備 🖼️**
  ```python
  response = requests.get(IMAGE_URL)
  img = Image.open(BytesIO(response.content))
  preprocess = weights.transforms()
  input_tensor = preprocess(img)
  input_batch = input_tensor.unsqueeze(0)
  ```
  ここでは、人間が見るための画像データを、AIが理解できる形式のデータに変換しています。
  *   `requests.get(...)` と `Image.open(...)`: `requests`ライブラリでURLから画像データをダウンロードし、`Pillow`ライブラリ（`PIL`としてインポート）で画像として開いています。
  *   `preprocess = weights.transforms()`: これもPyTorch Visionの素晴らしい機能です。先ほど指定した`weights`に紐付いた、**最適な前処理**を自動で取得してくれます。中身は「画像を224x224ピクセルにリサイズし、PyTorchが扱えるテンソル形式に変換し、最後に特定の値で色情報を正規化する」という一連の処理がまとまったものです。
  *   `input_tensor = preprocess(img)`: 実際に画像に前処理を適用します。
  *   `input_batch = input_tensor.unsqueeze(0)`: AIモデルは通常、複数の画像を一度に処理できるように設計されています（これを「バッチ処理」と呼びます）。今回は1枚の画像しか扱いませんが、モデルの入力形式に合わせるために、「1枚だけのバッチ」という形に次元を追加しています。これも一種のお作法です。

- **チャンク3: 推論の実行 🧠**
  ```python
  with torch.no_grad():
      output = model(input_batch)
  ```
  いよいよAIに画像を「見せて」、何だと思うか尋ねる部分です。
  *   `with torch.no_grad():`: 推論時には不要な勾配計算（学習時に使われる計算）をオフにするためのブロックです。これにより、メモリ使用量が減り、計算速度が向上します。推論時には必ずこのブロックで囲むようにしましょう。
  *   `output = model(input_batch)`: ここが核心部です。準備した画像データ（`input_batch`）をモデルに入力し、予測結果（`output`）を受け取っています。`output`の中身は、1000個の数値（ImageNetの1000クラスそれぞれに対する「スコア」）が入ったテンソルです。

- **チャンク4: 結果の解釈 🗣️**
  ```python
  probabilities = torch.nn.functional.softmax(output[0], dim=0)
  # ... (ラベルの取得) ...
  top5_prob, top5_catid = torch.topk(probabilities, 5)
  # ... (結果の表示) ...
  ```
  AIが出力したただの数値の羅列を、人間が理解できる「意味のある情報」に変換します。
  *   `torch.nn.functional.softmax(...)`: モデルが出力したスコアを、合計すると1（100%）になる「確率」に変換します。これにより、各クラスの確信度をパーセンテージで比較できるようになります。
  *   `labels = json.loads(...)`: ImageNetのクラスID（0〜999の数字）と、それに対応するクラス名（"Samoyed", "golden retriever"など）が書かれた対応表をWebからダウンロードしています。
  *   `torch.topk(probabilities, 5)`: 1000クラス分の確率の中から、最も確率が高い上位5つを、その確率（`top5_prob`）とクラスID（`top5_catid`）のセットで取り出します。
  *   `for`ループ: 取り出した上位5つの結果を、ラベル対応表を使って人間が読めるカテゴリ名に変換し、確率と一緒にきれいに表示しています。

***

### 5. ⚠️ 注意点またはヒント

PyTorch Visionは非常に強力ですが、初心者がハマりがちなポイントがいくつかあります。これだけは押さえておきましょう。

- **ヒント💡: 入力画像の「前処理」がAIの性能を左右する！**

初心者が最も陥りやすい罠は、**モデルが学習された時と異なる前処理を、推論時の画像に適用してしまうこと**です。AIモデルは非常に繊細で、学習時に見てきたデータと全く同じ形式（同じ画像サイズ、同じ色の正規化方法）のデータが入力されることを期待しています。

例えば、あるモデルが「すべての画像を256x256ピクセルにリサイズし、平均0.5、標準偏差0.5で正規化された」データで学習されたとします。もしあなたが推論時に画像を512x512ピクセルで入力したり、正規化を忘れたりすると、AIは混乱してしまい、全く見当違いな予測をしてしまいます。

**【解決策】**
幸いなことに、最近のPyTorch Visionではこの問題に対する素晴らしい解決策が用意されています。それがサンプルコードでも使った `weights.transforms()` です。

```python
# 悪い例：自分で前処理を定義すると、モデルと合わない可能性がある
# preprocess = transforms.Compose([
#     transforms.Resize(256),
#     transforms.CenterCrop(224),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
# ])

# 良い例：モデルに紐付いた最適な前処理を自動で取得する
weights = models.ResNet50_Weights.DEFAULT
preprocess = weights.transforms()
```
このように、`weights`オブジェクトから`transforms()`メソッドを呼び出すことで、その学習済みモデルに最適化された前処理パイプラインを間違いなく取得できます。自力で前処理を定義するのではなく、**常にこの方法を使う**ことを強くお勧めします。

***

### 6. 🔗 一緒に見ておくと良いライブラリ

PyTorch Visionの次に学ぶべきライブラリとして、ぜひ **OpenCV-Python (`opencv-python`)** をお勧めします。

- **OpenCV-Python (`opencv-python`)**
  *   **役割:** 高機能な画像・動画処理ライブラリ
  *   **PyTorch Visionとの関係:** PyTorch Visionが「学習済みモデルやデータセットを扱う」ことに特化しているのに対し、OpenCVは「画像や動画そのものを操作する」ための、より低レベルで多機能なツールです。
  *   **連携の例:**
      *   **前処理:** Webカメラからリアルタイムで映像を取得し、顔の部分だけを切り出してPyTorch Visionのモデルに入力する。
      *   **後処理:** PyTorch Visionの物体検出モデルが予測した結果（物体の位置を示す四角い枠の座標）を、OpenCVを使って元の画像に描画して可視化する。

PyTorch VisionがAIの「頭脳」なら、OpenCVは「目」や「手」のような役割を果たします。この二つを組み合わせることで、単なる予測だけでなく、インタラクティブで実践的なアプリケーションを構築する道が拓けます。

***

### 7. 🎉 まとめ

今回は、Pythonで画像認識を始める際の強力な味方、`PyTorch Vision`について詳しく見てきました。

- PyTorch Visionは、AI開発における**「高級料理キット」**であり、学習済みモデル、データセット、前処理ツールを提供してくれます。
- **画像分類**や**物体検出**といった高度なタスクを、驚くほど簡単なコードで実現できます。
- 特に**転移学習**の基盤として利用することで、少ないデータでも高性能な独自のAIモデルを効率的に開発できます。
- 使う上での最大のコツは、**モデルに合った正しい前処理 (`weights.transforms()`) を使うこと**です。

PyTorch Visionは、画像認識AIの世界への扉を開けてくれる、最高のガイドです。理論の学習で立ち止まってしまう前に、まずはこのライブラリを使って「動くもの」を作ってみることで、楽しさを実感し、学習のモチベーションを維持することができるでしょう。

**【今日の挑戦課題】**
さあ、次はあなたの番です！この記事で学んだことを使って、以下の課題に挑戦してみましょう。

1.  サンプルコードの `IMAGE_URL` を、あなたがインターネットで見つけた好きな動物、乗り物、食べ物などの画像のURLに変更して、AIが正しく認識できるか試してみてください。
2.  `model = models.resnet50(weights=weights)` の部分を、別のモデル、例えば `models.mobilenet_v3_large` や `models.efficientnet_b0` に書き換えてみましょう。モデルによって予測の精度や速度がどのように変わるか観察してみてください。（ヒント: `weights`もモデルに合わせて `models.MobileNet_V3_Large_Weights.DEFAULT` のように変更する必要があります）

Happy Coding!