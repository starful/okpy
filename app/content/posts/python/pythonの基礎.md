---
title: 'Pythonの基礎'
date: 2025-01-21
category: python
slug: pythonの基礎
summary: '<pPythonはその簡潔な構文と応用性から、初心者に最適なプログラミング言語です。以下では、Pythonのインストール方法から基本文法、最初のプログラム作成までを詳しく解説します。さらに、Python 3を基準にした基本文法の例を20個紹介し、学びを深めます。</p'
hatena_path: '/entry/2025/01/21/154018'
---

# Pythonの基礎

<p>Pythonはその簡潔な構文と応用性から、初心者に最適なプログラミング言語です。以下では、Pythonのインストール方法から基本文法、最初のプログラム作成までを詳しく解説します。さらに、Python 3を基準にした基本文法の例を20個紹介し、学びを深めます。</p>
<p><img src="https://media.discordapp.net/attachments/1329990548299448441/1331620507371573319/keru2106_high-level_general-purpose_programming_language._PIXAR_6d9b3dd2-c45b-4887-bd81-b8a4a4e2f8f6.png?ex=679247bd&amp;is=6790f63d&amp;hm=2ab9072475448dd96a2d98ce46b5f5c4ac1b8553f60f62d972b584db9b7999c7&amp;=&amp;format=webp&amp;quality=lossless&amp;width=550&amp;height=308" /></p>
<hr />
<p><strong>1. Pythonのインストールと環境構築</strong><br />Python 3を始めるには、インストールと環境設定が必要です。以下は主要OSごとのインストール手順です。</p>
<ul>
<li>
<p><strong>Windowsユーザー</strong>:<br />Python公式サイト（<a href="https://www.python.org/">python.org</a>）から最新のPython 3インストーラーをダウンロードし、「Add Python to PATH」にチェックを入れてインストールを完了します。その後、コマンドプロンプトで<code>python --version</code>を実行してインストールを確認します。</p>
</li>
<li>
<p><strong>Macユーザー</strong>:<br />Homebrewをインストール後、以下を実行します。</p>
<pre><code>brew install python
python3 --version
</code></pre>
</li>
<li>
<p><strong>Linuxユーザー</strong>:<br />ターミナルで以下を実行してインストールを完了します。</p>
<pre><code>sudo apt update
sudo apt install python3
python3 --version
</code></pre>
</li>
</ul>
<hr />
<p><strong>2. Python 3の基本文法</strong><br />以下は、Python 3を基準にした基本文法の具体例20個です。</p>
<ol>
<li><strong>変数とデータ型</strong></li>
</ol>
<pre><code class="language-python">name = "Alice"  # 文字列型
age = 25        # 整数型
height = 160.5  # 浮動小数点型
is_student = True  # 真偽値型

print(f"名前: {name}, 年齢: {age}, 身長: {height}cm, 学生: {is_student}")
</code></pre>
<ol start="2">
<li><strong>条件分岐</strong></li>
</ol>
<pre><code class="language-python">score = 85
if score &gt;= 90:
    print("優秀です！")
elif score &gt;= 70:
    print("よくできました！")
else:
    print("次はもっと頑張りましょう！")
</code></pre>
<ol start="3">
<li><strong>繰り返し処理</strong></li>
</ol>
<pre><code class="language-python"># forループ
for i in range(5):
    print(f"ループ回数: {i}")

# whileループ
count = 0
while count &lt; 3:
    print(f"カウント: {count}")
    count += 1
</code></pre>
<ol start="4">
<li><strong>リスト</strong></li>
</ol>
<pre><code class="language-python">fruits = ["apple", "banana", "cherry"]
fruits.append("orange")
print(fruits)

for fruit in fruits:
    print(f"I like {fruit}")
</code></pre>
<ol start="5">
<li><strong>辞書</strong></li>
</ol>
<pre><code class="language-python">person = {"name": "Alice", "age": 25, "city": "Tokyo"}
person["age"] = 26
print(person)
</code></pre>
<ol start="6">
<li><strong>関数</strong></li>
</ol>
<pre><code class="language-python">def greet(name):
    print(f"こんにちは, {name}さん！")

greet("Alice")
greet("Bob")
</code></pre>
<ol start="7">
<li><strong>リスト内包表記</strong></li>
</ol>
<pre><code class="language-python">numbers = [1, 2, 3, 4, 5]
squared = [n ** 2 for n in numbers]
print(squared)
</code></pre>
<ol start="8">
<li><strong>ファイル操作</strong></li>
</ol>
<pre><code class="language-python">with open("example.txt", "w") as file:
    file.write("Hello, Python!")

with open("example.txt", "r") as file:
    content = file.read()
    print(content)
</code></pre>
<ol start="9">
<li><strong>例外処理</strong></li>
</ol>
<pre><code class="language-python">try:
    number = int(input("数字を入力してください: "))
    print(f"入力された数字は {number} です。")
except ValueError:
    print("無効な入力です。数字を入力してください！")
</code></pre>
<ol start="10">
<li><strong>クラスとオブジェクト</strong></li>
</ol>
<pre><code class="language-python">class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        print(f"私は{self.name}、{self.age}歳です。")

person = Person("Alice", 25)
person.introduce()
</code></pre>
<ol start="11">
<li><strong>タプル</strong></li>
</ol>
<pre><code class="language-python">coordinates = (10, 20)
print(f"X: {coordinates[0]}, Y: {coordinates[1]}")
</code></pre>
<ol start="12">
<li><strong>セット</strong></li>
</ol>
<pre><code class="language-python">unique_numbers = {1, 2, 3, 4, 4, 5}
print(unique_numbers)
</code></pre>
<ol start="13">
<li><strong>スライス</strong></li>
</ol>
<pre><code class="language-python">numbers = [0, 1, 2, 3, 4, 5]
print(numbers[2:5])
</code></pre>
<ol start="14">
<li><strong>ラムダ関数</strong></li>
</ol>
<pre><code class="language-python">square = lambda x: x ** 2
print(square(5))
</code></pre>
<ol start="15">
<li><strong>マップ関数</strong></li>
</ol>
<pre><code class="language-python">numbers = [1, 2, 3, 4]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)
</code></pre>
<ol start="16">
<li><strong>フィルタ関数</strong></li>
</ol>
<pre><code class="language-python">numbers = [1, 2, 3, 4, 5, 6]
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print(even_numbers)
</code></pre>
<ol start="17">
<li><strong>zip関数</strong></li>
</ol>
<pre><code class="language-python">names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 88]
result = list(zip(names, scores))
print(result)
</code></pre>
<ol start="18">
<li><strong>文字列フォーマット</strong></li>
</ol>
<pre><code class="language-python">name = "Alice"
age = 25
print(f"My name is {name} and I am {age} years old.")
</code></pre>
<ol start="19">
<li><strong>正規表現</strong></li>
</ol>
<pre><code class="language-python">import re
text = "My phone number is 123-456-7890"
match = re.search(r"\d{3}-\d{3}-\d{4}", text)
if match:
    print(f"見つかった番号: {match.group()}")
</code></pre>
<ol start="20">
<li><strong>モジュールのインポート</strong></li>
</ol>
<pre><code class="language-python">import math
print(f"円周率: {math.pi}")
</code></pre>
<hr />
<p><strong>3. 最初のプログラムを作成する</strong><br />Python 3を使用して、最初に「Hello, World!」プログラムを作成してみましょう。</p>
<p>コード例:</p>
<pre><code class="language-python">print("Hello, World!")
</code></pre>
<p>ターミナルでこのプログラムを実行し、Pythonの動作を確認してください。</p>
<hr />
<p>これらの例を参考に、Python 3の基本をマスターし、次のステップとして簡単なプロジェクトに挑戦してみましょう！</p>
