---
category: python
cover: https://storage.googleapis.com/ok-project-assets/okpy/20250725152203.png
date: 2025-07-31
hatena_path: /entry/2025/07/31/183835
slug: 文章解析のスタート-python-nltk-ライブラリの魅力
summary: Python の nltk (自然言語処理ツールキット) は、文本解析に最適なライブラリです。文章分割、単語分割、哲学解析、木構造構文解析などが可能です。
title: '文章解析のスタート: Python nltk ライブラリの魅力'
---

# 文章解析のスタート: Python nltk ライブラリの魅力

# Python `nltk` ライブラリ完全ガイド

![image](https://storage.googleapis.com/ok-project-assets/okpy/20250725152203.png)

Python の `nltk` (自然言語処理ツールキット) は、文本解析に最適なライブラリです。文章分割、単語分割、哲学解析、木構造構文解析などが可能です。

## 1. `nltk` ライブラリの概要

* 文章分析に特化した自然言語処理ライブラリ
* 単語の正規化、哲学解析、連載構文解析など
* 論文の評価やテキスト分類などに役立つ

### **インストール方法**

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```sh
pip install nltk
```

</div>

---

## 2. 主な機能と使用例

### (1) コーパスの読み込み

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
```

</div>

### (2) 文を文章分割

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from nltk.tokenize import sent_tokenize
text = "NLTK is a powerful toolkit. It is widely used."
print(sent_tokenize(text))
```

</div>

### (3) 単語分割 (Tokenize)

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from nltk.tokenize import word_tokenize
print(word_tokenize(text))
```

</div>

### (4) 哲学解析 (POS tagging)

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from nltk import pos_tag
words = word_tokenize("Natural Language Toolkit")
print(pos_tag(words))
```

</div>

### (5) ステミング (語尾分削)

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()
print(stemmer.stem("running"))
```

</div>

### (6) レマティゼーション

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from nltk.stem import WordNetLemmatizer
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
print(lemmatizer.lemmatize("better", pos="a"))
```

</div>

### (7) ストップワードの除去

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from nltk.corpus import stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words("english"))
print([w for w in word_tokenize("This is a test.") if w not in stop_words])
```

</div>

### (8) N-gram 抽出

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from nltk import ngrams
sentence = "This is a simple sentence"
print(list(ngrams(word_tokenize(sentence), 2)))
```

</div>

### (9) 例題の分類

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
from nltk import NaiveBayesClassifier
train = [(dict(hungry=True), 'yes'), (dict(hungry=False), 'no')]
classifier = NaiveBayesClassifier.train(train)
print(classifier.classify(dict(hungry=True)))
```

</div>

### (10) 木構造解析

<div style="position: relative;"><button onclick="navigator.clipboard.writeText(this.nextElementSibling.innerText)" style="position: absolute; top: 5px; right: 5px; padding: 5px 10px; font-size: 12px; background-color: #007bff; color: white; border: none; cursor: pointer;">コピー</button>

```python
grammar = """
  NP: {<DT>?<JJ>*<NN>}
  VP: {<VB.*><NP|PP|CLAUSE>+$}
  PP: {<IN><NP>}
  CLAUSE: {<NP><VP>}
"""

cp = nltk.RegexpParser(grammar)
tree = cp.parse(pos_tag(word_tokenize("The quick brown fox jumps over the lazy dog")))
tree.draw()
```

</div>

---

## 3. `nltk` の主な機能

| 機能            | 説明             |
| ------------- | -------------- |
| Tokenize      | 文章分割や単語分割を行う   |
| POS Tagging   | 語類分析 (名詞、動詞 等) |
| Stopwords     | 意味の少ない言語の除去    |
| Stemming      | 単語を根語に変換       |
| Lemmatization | 語尾の正規化         |

---

## まとめ

`nltk` は自然言語処理のエントリーレベルライブラリです。
文章解析やテキスト分類、簡易検索エンジンを作成したい場面で最適です 🚀