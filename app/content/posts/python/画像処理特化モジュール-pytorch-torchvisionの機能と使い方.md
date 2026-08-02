---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250725151924.png
date: 2025-07-30
hatena_path: /entry/2025/07/30/124357
slug: 画像処理特化モジュール-pytorch-torchvisionの機能と使い方
summary: Python の torchvision は、PyTorch 環境での画像データの取り扱いを簡単にするためのライブラリです。画像データの前処理、データセットの読み込み、モデルの保存などが行えます。
title: 【PyTorch】torchvisionの使い方：画像前処理・データセット・モデルを網羅
description: PyTorchで画像処理をするならtorchvision。このガイドでは、画像前処理からモデル構築まで、実装に必要なすべての機能を解説します。実践的なコード例付きで、初心者でもすぐに使い始められます。
seo_title: torchvisionの使い方【初心者向け完全ガイド】PyTorchで画像処理を実装する方法 — OKPy
seo_description: PyTorchのtorchvisionで画像処理をマスター。前処理・データセット・モデルの使い方を実装例で解説。初心者から実践レベルまで対応。
---



# 画像処理特化モジュール：PyTorch torchvisionの機能と使い方

# Python `torchvision` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250725151924.png)

Python の `torchvision` は、PyTorch 環境での画像データの取り扱いを簡単にするためのライブラリです。画像データの前処理、データセットの読み込み、モデルの保存などが行えます。

## 1. `torchvision` ライブラリの概要

* PyTorch の画像処理特化モジュールグループ
* CIFAR10、MNIST、ImageNet などのデータセットを使用可能
* 変換、機械学習の前処理ステップを提供

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install torchvision
```

</div>

---

## 2. 主な機能と使用例

### (1) データセットの読み込み (CIFAR10)

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from torchvision import datasets, transforms

dataset = datasets.CIFAR10(root="./data", download=True, transform=transforms.ToTensor())
```

</div>

### (2) 変換の定義

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
transform = transforms.Compose([
    transforms.Resize(32),
    transforms.CenterCrop(28),
    transforms.ToTensor()
])
```

</div>

### (3) DataLoader の使用

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from torch.utils.data import DataLoader

loader = DataLoader(dataset, batch_size=64, shuffle=True)
```

</div>

### (4) データの表示

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import matplotlib.pyplot as plt
import numpy as np

images, labels = next(iter(loader))
plt.imshow(np.transpose(images[0], (1, 2, 0)))
plt.title(f"Label: {labels[0]}")
plt.show()
```

</div>

### (5) torchvision.models の利用 (ResNet18)

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from torchvision import models

model = models.resnet18(pretrained=True)
print(model)
```

</div>

### (6) transforms.RandomHorizontalFlip()

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor()
])
```

</div>

### (7) torchvision.utils.make\_grid()

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from torchvision.utils import make_grid

grid_img = make_grid(images[:4])
plt.imshow(np.transpose(grid_img, (1, 2, 0)))
plt.show()
```

</div>

### (8) torchvision.io 画像読み込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from torchvision.io import read_image

img = read_image("sample.jpg")
print(img.shape)
```

</div>

### (9) torchvision.transforms.Normalize

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])
```

</div>

### (10) torchvision.transforms.RandomRotation

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
transform = transforms.Compose([
    transforms.RandomRotation(30),
    transforms.ToTensor()
])
```

</div>

---

## 3. `torchvision` の主なモジュール

| 機能           | 説明                               |
| ------------ | -------------------------------- |
| `datasets`   | CIFAR10, MNIST などのデータ読み込み        |
| `transforms` | 画像変換処理 (トリミング、抽出、Tensor 化)       |
| `models`     | ResNet などの先端機械学習モデル              |
| `utils`      | make\_grid, save\_image などの補助ツール |
| `io`         | 画像ファイルの読み込みや保存                   |

---

## まとめ

`torchvision` は PyTorch の画像処理を支える強力なライブラリです。
データ読み込み、変換、モデル読み込みなどが容易になり、実践的なデータ分類モデル開発を助けます 🚀