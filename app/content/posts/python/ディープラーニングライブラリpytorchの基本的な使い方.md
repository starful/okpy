---
category: python
date: 2025-04-08
hatena_path: /entry/2025/04/08/062047
slug: ディープラーニングライブラリpytorchの基本的な使い方
summary: PyTorchの基本から実装まで、コード例付きで完全に解説。テンソル操作、ニューラルネットワーク構築、GPU活用により初心者も今すぐディープラーニング開発を始められます。
title: PyTorchで始めるディープラーニング│テンソル・GPU・訓練ループを初心者向けに解説
description: PyTorch初心者向け完全ガイド。テンソルからGPU、訓練ループまで実装解説。
seo_title: PyTorchで始めるディープラーニング│テンソル・GPU・訓練ループを初心者向けに解説
seo_description: PyTorch初心者向け完全ガイド。テンソル操作からGPU活用、モデル訓練まで実装可能。難しい理論は不要です。
---
🚀 **なぜPyTorchを学ぶ必要があるのか？**

研究から実務まで、AI・機械学習の現場で最も使われているディープラーニングフレームワークです。本記事では、面倒な環境構築や難しい理論は一切スキップし、わずか数行のコードでテンソル操作からGPU活用、モデル訓練までを実装していきます。

PyTorchは研究から実務まで広く使われているディープラーニングライブラリです。本記事ではゼロから始める方向けに、テンソル操作の基礎、ニューラルネットワークの構築、GPU活用、そして訓練ループの実装までをコード例付きで解説します。

# ディープラーニングライブラリPyTorchの基本的な使い方

# Python `PyTorch` ライブラリ完全ガイド

`PyTorch` はFacebookによって開発されたオープンソースのディープラーニングライブラリで、柔軟性と使いやすさを兼ね備えています。研究用途から本番環境まで幅広く活用されており、動的計算グラフによって直感的な開発が可能です。本記事では、Pythonを用いた`PyTorch`の基本的な使い方を、コピー可能なコード付きで紹介します。

## 1. `PyTorch` の概要

- 動的計算グラフによる柔軟なモデリング
- GPU（CUDA）による高速処理対応
- `torch.nn`、`torch.optim`、`torch.utils.data`など豊富なサブモジュール

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install torch torchvision
```
</div>

---

## 2. 主な機能と使用例

### (1) テンソルの作成と演算

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import torch

a = torch.tensor([1.0, 2.0])
b = torch.tensor([3.0, 4.0])
print(a + b)
```
</div>

### (2) GPU 上での演算

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
a = torch.rand(3, 3).to(device)
print(a)
```
</div>

### (3) ニューラルネットワークの定義（nn.Module）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import torch.nn as nn

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 2)
    def forward(self, x):
        return self.fc(x)
```
</div>

### (4) 損失関数と最適化（optimizer）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
model = Net()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
```
</div>

### (5) データセットとデータローダー

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from torch.utils.data import DataLoader, TensorDataset

dataset = TensorDataset(torch.randn(100, 10), torch.randint(0, 2, (100,)))
dataloader = DataLoader(dataset, batch_size=32)
```
</div>

### (6) 学習ループの記述

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
for epoch in range(5):
    for x_batch, y_batch in dataloader:
        optimizer.zero_grad()
        outputs = model(x_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1}: Loss = {loss.item()}")
```
</div>

### (7) 推論と精度評価

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
with torch.no_grad():
    y_pred = model(torch.randn(10, 10))
    predicted_classes = torch.argmax(y_pred, dim=1)
    print(predicted_classes)
```
</div>

### (8) モデルの保存と読み込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
torch.save(model.state_dict(), "model.pth")
model.load_state_dict(torch.load("model.pth"))
```
</div>

### (9) モデルをエクスポート（ONNX）

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
dummy_input = torch.randn(1, 10)
torch.onnx.export(model, dummy_input, "model.onnx")
```
</div>

### (10) Autograd による勾配計算

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
x = torch.tensor([2.0], requires_grad=True)
y = x ** 2
y.backward()
print(x.grad)
```
</div>

---

## 3. `PyTorch` の主な機能まとめ

| 機能 | 説明 |
|------|------|
| `torch.Tensor` | NumPy互換のテンソル構造。GPU演算が可能 |
| `torch.nn` | モデル構築用の層・損失関数などを提供 |
| `torch.optim` | 最適化アルゴリズム（SGD、Adamなど） |
| `DataLoader` | バッチ処理とシャッフルを自動化 |
| `Autograd` | 自動微分による勾配計算をサポート |

---

## まとめ

`PyTorch`は、柔軟性・可読性・拡張性に優れたディープラーニングライブラリとして、研究者・実務者を問わず高く評価されています。直感的なコーディングでありながら高度なカスタマイズも可能なため、深層学習を学ぶならまず習得したいライブラリの一つです。
