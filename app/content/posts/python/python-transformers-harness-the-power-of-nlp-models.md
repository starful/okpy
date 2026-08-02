---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250725153049.png
date: 2025-08-06
hatena_path: /entry/2025/08/06/100603
slug: python-transformers-harness-the-power-of-nlp-models
summary: Python の transformers は、自然言語処理 (NLP) モデルを簡単に使用できるようにする Hugging Face 社の強力なライブラリです。
title: 'Python Transformers: Harness the Power of NLP Models'
---

# Python Transformers: Harness the Power of NLP Models

# Python `transformers` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250725153049.png)

Python の `transformers` は、自然言語処理 (NLP) モデルを簡単に使用できるようにする Hugging Face 社の強力なライブラリです。
事前学習済みの BERT、GPT、T5、RoBERTa などのモデルを簡単に利用できます。

## 1. `transformers` ライブラリの概要

* BERT や GPT などの事前学習済みモデルを即利用可能
* テキスト分類、要約、翻訳、質問応答など幅広い NLP タスクに対応
* PyTorch および TensorFlow の両方に対応

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install transformers
```

</div>

---

## 2. 主な機能と使用例（10選）

### (1) テキスト分類モデルの読み込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from transformers import pipeline
classifier = pipeline("sentiment-analysis")
print(classifier("I love using transformers!"))
```

</div>

### (2) テキスト要約

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
summarizer = pipeline("summarization")
print(summarizer("Transformers is a library by Hugging Face..."))
```

</div>

### (3) 翻訳

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
translator = pipeline("translation_en_to_fr")
print(translator("I love natural language processing."))
```

</div>

### (4) 質問応答

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
qa = pipeline("question-answering")
result = qa(question="What is Transformers?", context="Transformers is a library from Hugging Face.")
print(result)
```

</div>

### (5) テキスト生成 (GPT)

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
generator = pipeline("text-generation", model="gpt2")
print(generator("The future of AI is", max_length=30))
```

</div>

### (6) 固有表現抽出 (NER)

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
ner = pipeline("ner", grouped_entities=True)
print(ner("Hugging Face Inc. is a company based in New York City."))
```

</div>

### (7) モデルの保存と読み込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from transformers import AutoModel
model = AutoModel.from_pretrained("bert-base-uncased")
model.save_pretrained("./bert")
```

</div>

### (8) トークナイザーの利用

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
tokens = tokenizer("Hello, world!", return_tensors="pt")
print(tokens)
```

</div>

### (9) モデルのパイプラインを自作

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from transformers import AutoModelForSequenceClassification
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")
```

</div>

### (10) トークナイズ結果のデコード

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
input_ids = tokenizer("Transformers are amazing!", return_tensors="pt")["input_ids"]
print(tokenizer.decode(input_ids[0]))
```

</div>

---

## 3. `transformers` の主な機能

| 機能              | 説明              |
| --------------- | --------------- |
| `pipeline`      | 主要タスクの一括呼び出しが可能 |
| `AutoModel`     | モデルの自動ダウンロード・利用 |
| `AutoTokenizer` | トークナイザーの読み込み    |
| `Trainer`       | 学習用ツール          |

---

## まとめ

`transformers` は、最新の自然言語処理技術を手軽に扱うための強力なライブラリです。
モデルの呼び出し、テキスト処理、トレーニングが簡単にできるため、初心者から上級者まで幅広く活用できます 🚀