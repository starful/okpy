---
title: 'Terraform Locals Deep Dive: ローカル値合成パターンで重複を削減する実践ガイド'
date: 2026-10-19
category: terraform
slug: terraform-locals-deep-dive-reducing-duplication-with-local-value-composition-pat
summary: 'Terraform で構成が肥大化してくると、同じ式やタグ定義、命名規則が複数のリソースブロックに散在し始める。`local` 値はこの重複を一箇所に集約するための基本機能だが、単純な変数置き換えとしてしか使われていないケースが多い。本記事では、`locals` ブロックを「合成可能な中間レイヤー」として設計し、…'
lang: ja
---

# Terraform Locals Deep Dive: ローカル値合成パターンで重複を削減する実践ガイド

Terraform で構成が肥大化してくると、同じ式やタグ定義、命名規則が複数のリソースブロックに散在し始める。`local` 値はこの重複を一箇所に集約するための基本機能だが、単純な変数置き換えとしてしか使われていないケースが多い。本記事では、`locals` ブロックを「合成可能な中間レイヤー」として設計し、重複を削減しつつ可読性とメンテナンス性を両立させる実践パターンを解説する。

## locals の基本概念を再確認する

`locals` ブロックは、モジュール内でのみ有効な名前付き値を定義する機能であり、`variable` のように外部から注入されるものではなく、`output` のように外部へ公開されるものでもない。あくまでモジュール内部の「計算結果のキャッシュ」として振る舞う。

```hcl
locals {
  environment = terraform.workspace
  name_prefix = "${var.project}-${local.environment}"
}
```

重要な特性は次の3点である。

1. **宣言順に依存しない**: `locals` ブロック内の値は、Terraform がグラフ解析によって依存関係を自動的に解決するため、定義順は実行順序に影響しない。
2. **複数の `locals` ブロックを定義できる**: 論理的なグルーピングのために、ファイルを分けて複数の `locals {}` を書いても問題ない。
3. **式のみで、副作用を持たない**: `local` は値であり、リソースのように `create_before_destroy` などのライフサイクルを持たない。そのため値の再計算は常に決定的になる。

## 合成パターン:ローカル値を積み上げて設計する

重複削減の核心は、「小さな locals を定義し、それらを組み合わせてより大きな locals を作る」という合成的な設計である。典型的な例がタグ管理だ。

```hcl
locals {
  common_tags = {
    Project     = var.project
    Environment = terraform.workspace
    ManagedBy   = "terraform"
  }

  cost_tags = {
    CostCenter = var.cost_center
    Owner      = var.owner
  }

  # 合成:複数の locals を merge して最終形を作る
  resource_tags = merge(
    local.common_tags,
    local.cost_tags,
    { Name = "${local.name_prefix}-ec2" }
  )
}

resource "aws_instance" "web" {
  # ...
  tags = local.resource_tags
}
```

このように、`merge()` や `concat()`、三項演算子を使って「部品となる locals」を組み合わせることで、各リソースブロック側は `tags = local.resource_tags` の一行で済む。タグ要件が追加された場合も、変更箇所は `locals` ブロックの一箇所に限定される。

### 条件分岐を locals に閉じ込める

環境ごとに異なる設定値(インスタンスサイズ、レプリカ数など)をリソースブロック内で `count` や `?:` を使って直接書くと、リソース定義が読みにくくなる。これを locals に委譲する。

```hcl
locals {
  env_config = {
    dev     = { instance_type = "t3.micro",  min_size = 1, max_size = 2 }
    staging = { instance_type = "t3.small",  min_size = 2, max_size = 4 }
    prod    = { instance_type = "m5.large",  min_size = 3, max_size = 10 }
  }

  current_config = local.env_config[terraform.workspace]
}

resource "aws_launch_template" "app" {
  instance_type = local.current_config.instance_type
}

resource "aws_autoscaling_group" "app" {
  min_size = local.current_config.min_size
  max_size = local.current_config.max_size
}
```

map によるルックアップパターンは、環境分岐を `locals` の宣言的なデータ構造に落とし込み、リソースブロックからロジックを排除できる点が利点である。環境が増えても `env_config` に1行追加するだけで済む。

### for 式による変換の合成

リスト・マップの変換処理も locals に切り出すべき典型例である。

```hcl
variable "subnets" {
  type = list(object({
    name = string
    cidr = string
    az   = string
  }))
}

locals {
  subnet_map = {
    for s in var.subnets :
    s.name => {
      cidr = s.cidr
      az   = s.az
      tags = merge(local.common_tags, { Tier = s.name })
    }
  }
}

resource "aws_subnet" "this" {
  for_each          = local.subnet_map
  cidr_block        = each.value.cidr
  availability_zone = each.value.az
  tags              = each.value.tags
}
```

`for_each` と組み合わせることで、入力データの形を locals 側で正規化し、リソース側は構造が整った `each.value` を消費するだけになる。入力バリデーションや変換ロジックが複雑な場合は、`locals` を段階的に分割する(例: `local.raw_subnets` → `local.validated_subnets` → `local.subnet_map`)ことで、各段階が単体で読める粒度に保てる。

## state との関係

`locals` の値は Terraform の state ファイルに直接「リソースとして」記録されるわけではないが、その計算結果はリソースの属性値として state に反映される。つまり `local.resource_tags` の中身が変わればそれを参照しているリソースの `tags` 属性が変わり、結果として plan に差分が出る。

ここで注意すべきは、**locals 自体に life cycle や state アドレスは存在しない**という点だ。`terraform state list` に `local.xxx` が出てくることはない。リファクタリングで locals の構造を変えても、それを参照しているリソースの属性値が変わらない限り、plan は no-op になる。逆に、`for_each` のキー生成に locals を使っている場合、locals の計算結果(キーの文字列)が変わると、Terraform はリソースの「追加・削除」と解釈してしまう。

```hcl
# 危険な例:workspace 名を含めるとキーが変わり、リソースが re-create される
locals {
  subnet_map = {
    for s in var.subnets : "${terraform.workspace}-${s.name}" => s
  }
}
```

`for_each` のキーに揺れやすい値(タイムスタンプ、workspace 名、環境変数など)を混ぜると、意図しない destroy/create が発生するため、キーは安定した識別子(name や id)に限定するべきである。

## モジュールでの locals 設計

モジュール境界を越えて locals を公開することはできない。モジュール内部の `locals` は呼び出し元から不可視であり、必要な値は明示的に `output` として公開する必要がある。

```hcl
# modules/network/main.tf
locals {
  vpc_cidr_blocks = [for cidr in var.cidr_ranges : cidrsubnet(var.base_cidr, 4, cidr)]
}

output "subnet_cidrs" {
  value = local.vpc_cidr_blocks
}
```

モジュール設計における locals のベストプラクティスは以下の通り。

- **「入力の正規化」はモジュール先頭の locals に集約する**: `var.*` を直接複数箇所で参照せず、一度 locals で検証・デフォルト値補完してから使う。
- **「出力の整形」は末尾の locals に集約する**: output ブロックの式を複雑にせず、`local.output_xxx` を経由させることで、output ブロック自体はシンプルな参照のみにする。
- **モジュール間で同じ locals パターンを共有したい場合は、`locals` を変数化するのではなく、共通ロジックをモジュール自体として切り出す**: locals はモジュールをまたいで再利用できない機能だからである。

## 注意点

- **過度な合成は可読性を損なう**: locals を5段階以上積み重ねると、最終的な値がどう組み立てられているかを追うのに `terraform console` を使わざるを得なくなる。2〜3段階を目安にし、複雑になりすぎたらモジュール分割を検討する。
- **循環参照はエラーになる**: `local.a` が `local.b` を参照し、`local.b` が `local.a` を参照すると、Terraform は依存関係グラフでサイクルを検出してエラーを出す。合成的な設計をするほどこのリスクは高まるため、各 locals が「一方向に積み上がる」ように設計する。
- **sensitive な値の扱い**: `local` ブロックの値自体に `sensitive` 属性を直接付与することはできない(Terraform 1.x 時点)。機密値を扱う場合は、変数側で `sensitive = true` を設定し、その変数を参照する locals も自動的に sensitive として扱われる点を理解しておく。
- **`terraform console` でのデバッグ**: 複雑な locals の合成結果を確認する際は、`terraform console` 内で `local.resource_tags` のように直接評価すると実際の計算結果を確認できる。plan を都度実行するより高速にデバッグできる。

## クラウドプロバイダーとの関係

`locals` 自体はプロバイダー非依存の Terraform コア機能であり、AWS・GCP・Azure のどのプロバイダーを使っていても同じ書き方になる。ただし実務上の使われ方には差がある。

- **AWS**: タグ戦略(`common_tags` の合成)や、リージョン・AZ ごとのパラメータテーブルを locals の map で表現するケースが非常に多い。`aws_caller_identity` や `aws_region` などのデータソースの結果を locals で加工して再利用するパターンも定番である。
- **GCP**: プロジェクトID・ネットワーク命名規則(`project-env-service` のような規則)を locals で一元化し、`google_project` や `google_compute_network` など複数リソースで共有することが多い。
- **Azure**: リソースグループ名やロケーションのマッピングを locals の map で管理し、`azurerm` プロバイダーの命名規則の制約(長さ制限や許可文字種)に対応するための文字列加工(`lower()`, `substr()` など)を locals に集約するパターンが見られる。

いずれのプロバイダーでも、「命名規則」「タグ/ラベル」「環境別パラメータ」の3種類が locals 合成の主戦場になる点は共通している。

## FAQ

**Q1. `locals` と `variable` はどう使い分けるべきか?**
`variable` は呼び出し元(root module やモジュール利用者)からの入力を受け取るためのインターフェースであり、`locals` はモジュール内部でのみ使う計算結果である。外部から変更してほしい値は `variable`、内部ロジックの結果としてのみ存在する値は `locals` に置く、という基準で判断する。入力値をそのまま使わず、デフォルト値の補完や文字列結合を行う場合は、必ず一度 `locals` を経由させるのが安全である。

**Q2. locals を使いすぎると plan の実行速度に影響するか?**
locals は単なる式評価であり、リソースのように API 呼び出しを伴わないため、数百個程度の locals であれば実行速度への影響は無視できるレベルである。ただし、`for` 式の中で別の `for` 式をネストしすぎたり、大きなリストに対して `cidrsubnet()` のような計算コストのある関数を繰り返し呼ぶ場合は、plan 時間が伸びることがある。パフォーマンスより先に可読性を優先し、問題が実測された場合にのみ最適化を検討すべきである。

**Q3. モジュール間で同じ locals の定義を共有したいが、どうすればよいか?**
`locals` ブロック自体はモジュールをまたいで import・共有することができない機能である。同じ命名規則やタグ合成ロジックを複数モジュールで使いたい場合は、(1) 共通ロジックを `variable` として受け取り各モジュール内で同じ locals 式を再実装する、または(2)ロジックそのものを小さな「ユーティリティモジュール」として切り出し、`output` を通じて計算済みの値を各モジュールに渡す、のいずれかを選択する。ロジックが複雑であれば後者の方が重複削減効果が高い。

---

`locals` は単体で見ると地味な機能だが、「小さな部品を合成して最終形を作る」という設計思想を徹底することで、タグ管理・命名規則・環境別パラメータといった Terraform コードで繰り返し発生する重複を大幅に削減できる。合成の段数と循環参照のリスクに注意しながら、モジュール境界を意識した locals 設計を心がけたい。
