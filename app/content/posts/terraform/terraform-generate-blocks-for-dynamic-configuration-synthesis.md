---
title: 'Terraform generate ブロックで実現する動的設定合成'
date: 2026-10-01
category: terraform
slug: terraform-generate-blocks-for-dynamic-configuration-synthesis
summary: 'Terraform 0.14 以降で導入された `generate` に類する仕組み、とりわけ近年注目されている「設定合成（configuration synthesis）」のアプローチは、静的な HCL 記述だけでは対応しきれない大規模インフラ構成の課題を解決する手段として急速に普及しています。本稿では、Ter…'
lang: ja
---

# Terraform generate ブロックで実現する動的設定合成

## はじめに

Terraform 0.14 以降で導入された `generate` に類する仕組み、とりわけ近年注目されている「設定合成（configuration synthesis）」のアプローチは、静的な HCL 記述だけでは対応しきれない大規模インフラ構成の課題を解決する手段として急速に普及しています。本稿では、Terraform における generate ブロック的なパターン（`for_each` や `dynamic` ブロック、外部データソースと組み合わせた動的生成）を軸に、概念整理から実践的な HCL 例、state への影響、モジュール設計、運用上の注意点までを体系的に解説します。

なお「generate ブロック」という用語は、Terraform 本体の予約語というよりも、Terraform エコシステム全体（CDKTF の `generate` コマンド、Terragrunt の `generate` ブロック、プロバイダ定義の自動生成ツールなど）で使われる概念の総称として扱われることが多い点に注意してください。本稿では主に以下の3つの文脈を区別しながら説明します。

1. Terraform 本体の `dynamic` ブロックによる動的構成生成
2. Terragrunt の `generate` ブロックによるファイル合成
3. CDKTF の `cdktf generate` によるプロバイダ/モジュールコード生成

## 1. 概念: なぜ動的設定合成が必要か

従来の Terraform では、リソースの数や属性はコードに直接書き下す必要がありました。しかし実運用では以下のような要求が頻繁に発生します。

- 環境ごと（dev/stg/prod）にリソース数や設定値が異なる
- 外部システム（CMDB、Vault、設定ファイル）から取得した値に応じてブロック構成を変える
- 複数プロバイダ（AWS、GCP、Azure）にまたがる似た構成をテンプレート的に展開する
- ネストしたブロック（セキュリティグループのルールなど）を可変長で生成する

これらを実現するために、Terraform は `dynamic` ブロックと `for_each`/`count` による繰り返し生成の仕組みを提供しています。さらに Terragrunt では `generate` ブロックを使い、HCL ファイル自体を実行前に動的生成することで、プロバイダ定義やバックエンド設定を DRY に保つアプローチが一般的です。

「設定合成」というキーワードは、これらの仕組みを組み合わせて「人間が1行ずつ書く」のではなく「ルールとデータから構成を導出する」設計思想を指します。

## 2. dynamic ブロックによる動的生成の基本

Terraform の `dynamic` ブロックは、リスト型やマップ型の変数をもとにネストしたブロックを繰り返し生成します。

```hcl
variable "ingress_rules" {
  type = list(object({
    description = string
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
  }))
  default = []
}

resource "aws_security_group" "app" {
  name        = "app-sg"
  description = "Dynamically generated security group"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      description = ingress.value.description
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

この例では `ingress_rules` に渡すリストの要素数に応じて `ingress` ブロックが合成されます。ポイントは以下の通りです。

- `dynamic` のラベル（ここでは `"ingress"`）は、生成したいネストブロック名と一致させる
- `for_each` には list または map を渡せる（map の場合はキーも参照可能）
- `content` 内で `ingress.value`（イテレータ名.value）として要素にアクセスする
- イテレータ名は `iterator` 引数で変更可能（ネストした `dynamic` を使う際に名前衝突を避けるため推奨）

### ネストした dynamic ブロックの例

```hcl
dynamic "ingress" {
  for_each = var.ingress_rules
  iterator = rule
  content {
    description = rule.value.description
    from_port   = rule.value.from_port
    to_port     = rule.value.to_port
    protocol    = rule.value.protocol
    cidr_blocks = rule.value.cidr_blocks

    dynamic "self" {
      for_each = rule.value.self_reference ? [1] : []
      content {
        self = true
      }
    }
  }
}
```

このように `iterator` を明示することで、入れ子になった `dynamic` ブロック同士の変数名衝突を防げます。

## 3. for_each と count による構成合成

`dynamic` ブロックはリソース内部のネストブロックを対象としますが、リソース自体を複数生成する場合は `for_each` または `count` を使います。

```hcl
variable "buckets" {
  type = map(object({
    versioning_enabled = bool
    force_destroy       = bool
  }))
}

resource "aws_s3_bucket" "this" {
  for_each      = var.buckets
  bucket        = each.key
  force_destroy = each.value.force_destroy
}

resource "aws_s3_bucket_versioning" "this" {
  for_each = { for k, v in var.buckets : k => v if v.versioning_enabled }
  bucket   = aws_s3_bucket.this[each.key].id
  versioning_configuration {
    status = "Enabled"
  }
}
```

ここで注目すべきは `for` 式によるフィルタリングです。`var.buckets` から `versioning_enabled = true` の要素だけを抽出し、別リソースの `for_each` に渡しています。これにより「条件に応じたリソースの合成」という、generate 的な設計思想を Terraform 単体で実現できます。

## 4. Terragrunt の generate ブロック

複数環境・複数リージョンで同じプロバイダ設定やバックエンド設定を使い回す場合、Terragrunt の `generate` ブロックが有効です。

```hcl
# terragrunt.hcl
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.aws_region}"
  default_tags {
    tags = {
      Environment = "${local.env}"
      ManagedBy   = "terragrunt"
    }
  }
}
EOF
}

generate "backend" {
  path      = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
terraform {
  backend "s3" {
    bucket         = "${local.state_bucket}"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "${local.aws_region}"
    dynamodb_table = "${local.lock_table}"
    encrypt        = true
  }
}
EOF
}
```

`generate` ブロックは `terragrunt plan/apply` 実行時に `.tf` ファイルを物理的に書き出します。`if_exists` の挙動（`overwrite`、`overwrite_terragrunt`、`skip`、`error`）を理解しておくことが重要で、手動編集済みのファイルを誤って上書きしないよう `overwrite_terragrunt`（Terragrunt 生成のファイルのみ上書き）を選ぶのが安全です。

## 5. CDKTF による generate とコード生成

TypeScript や Python で Terraform を記述する CDKTF では、`cdktf get`（旧 `cdktf generate`）コマンドでプロバイダ・モジュールの型定義を自動生成します。

```bash
cdktf get
```

生成された `.gen/providers/aws` 配下のコードを使うことで、以下のように型安全に動的構成を組み立てられます。

```typescript
const rules = [
  { fromPort: 80, toPort: 80, protocol: "tcp" },
  { fromPort: 443, toPort: 443, protocol: "tcp" },
];

new SecurityGroup(this, "app", {
  vpcId: vpc.id,
  ingress: rules.map((r) => ({
    fromPort: r.fromPort,
    toPort: r.toPort,
    protocol: r.protocol,
    cidrBlocks: ["0.0.0.0/0"],
  })),
});
```

CDKTF は最終的に HCL ではなく JSON 形式の Terraform 構成（`cdktf.json` 経由で `cdktf.out` に合成）を生成します。プログラミング言語のループ・条件分岐をそのまま使えるため、HCL の `dynamic` ブロックよりも複雑な合成ロジックを書きやすい反面、生成物のレビューがしづらくなるトレードオフがあります。

## 6. state への影響

動的生成されたリソースは、Terraform の state 上では通常のリソースと同様にアドレス（`resource_type.resource_name[key]`）で管理されます。ただし運用上、以下の点に注意が必要です。

- **for_each のキー変更はリソースの再作成を招く**: map のキーを変更すると、Terraform はそれを「削除して新規作成」と解釈します。`terraform state mv` で対応するか、`moved` ブロックを使って意図を明示しましょう。

```hcl
moved {
  from = aws_s3_bucket.this["old-key"]
  to   = aws_s3_bucket.this["new-key"]
}
```

- **count から for_each への移行は破壊的**: `count` はインデックス番号でリソースを識別するため、要素の順序が変わると意図しない差分（削除・再作成）が発生します。可能な限り `for_each` を使う方が state の安定性が高くなります。
- **dynamic ブロックは state に直接現れない**: `dynamic` ブロックはあくまで HCL の構文糖衣であり、生成されたネストブロックの内容はリソースの属性として state に格納されます。したがって `dynamic` の有無による state の構造差分はありません。
- **Terragrunt の generate ファイルは state とは独立**: `generate` で書き出された `.tf` ファイルはプラン・適用のたびに再生成されるため、Git にコミットしない運用が一般的です（`.gitignore` に追加）。

## 7. モジュール設計との関係

動的設定合成はモジュール設計と密接に関わります。推奨されるパターンは以下の通りです。

```hcl
module "security_groups" {
  source = "./modules/security-group"

  for_each = var.environments

  name          = "${each.key}-sg"
  ingress_rules = each.value.ingress_rules
  vpc_id        = module.vpc[each.key].vpc_id
}
```

モジュール自体に `for_each` を適用することで、環境単位・サービス単位での合成が可能になります。設計上のベストプラクティスは次の通りです。

- 入力変数の型を `object` で厳密に定義し、合成ロジックの前提を明確にする
- 複雑な変換ロジックは `locals` にまとめ、リソースブロック内に直接書かない
- 合成に使うデータ（JSON/YAML設定ファイルなど）は `yamldecode`/`jsondecode` で読み込み、バリデーションを `variable` の `validation` ブロックで行う

```hcl
variable "ingress_rules" {
  type = list(object({
    from_port = number
    to_port   = number
    protocol  = string
  }))

  validation {
    condition     = alltrue([for r in var.ingress_rules : r.from_port <= r.to_port])
    error_message = "from_port は to_port 以下である必要があります。"
  }
}
```

## 8. AWS / GCP / Azure との関係

動的設定合成のパターンはプロバイダを問わず有効ですが、各クラウドで扱うリソースの性質により使いどころが異なります。

- **AWS**: セキュリティグループのルール、IAM ポリシーステートメント、ALB のリスナールールなど、可変長のネストブロックが多く、`dynamic` ブロックの恩恵を最も受けやすい領域です。
- **GCP**: `google_compute_firewall` のルールや `google_project_iam_binding` のメンバーリストなど、同様に可変長構成が多いですが、GCP の IAM は「バインディング単位」での管理が推奨されるため、`for_each` によるリソース単位の合成と相性が良い設計になっています。
- **Azure**: NSG（ネットワークセキュリティグループ）のルールや Azure Policy の割り当てなど、AWS と似た合成パターンが使えます。ただし Azure Provider はリソースごとに必須属性が多く、合成ロジックが複雑化しやすいため、`locals` での前処理を厚めに行うのが実践的です。

マルチクラウド構成では、プロバイダごとに異なるスキーマを吸収するために、共通の入力スキーマ（例: `ingress_rules`)を定義し、プロバイダ固有のモジュール内で `dynamic` ブロックに変換する「アダプタパターン」が有効です。

## 9. 注意点とアンチパターン

- **過度な抽象化を避ける**: すべてを変数駆動にしすぎると、HCL を読むだけでは実際に何が生成されるか分からなくなります。`terraform plan` の出力やドキュメントで可視化する運用を併用しましょう。
- **for_each のキーに計算結果を使わない**: `for_each` のキーはプラン時に確定している必要があります。`uuid()` や他リソースの計算結果に依存するキーは「既知でない値」エラーの原因になります。
- **Terragrunt generate の二重管理に注意**: 手動で編集可能な `.tf` ファイルと `generate` で自動生成されるファイルが混在すると、どちらが正なのか分からなくなります。生成対象ファイルは `.gitignore` に入れ、ソースは `terragrunt.hcl` 側に一元化しましょう。
- **CDKTF の生成コードをコミットする範囲を決める**: `.gen` ディレクトリはプロバイダバージョンに依存するため、CI でビルド時に `cdktf get` を実行する運用とリポジトリに含める運用のどちらかを明確にチーム内で合意してください。
- **動的生成とドリフト検知**: 外部データソース（`data` ブロックや `external` プロバイダ)をもとに合成した構成は、外部システム側の値が変わるたびに plan 差分が出ます。意図しない drift を避けるため、取得元データの変更頻度と Terraform 実行タイミングを合わせる設計が必要です。

## 10. FAQ

**Q1. dynamic ブロックと for_each（リソースレベル）の使い分けは？**

A. `for_each`（リソースレベル）は「リソースそのものを複数作る」ために使い、`dynamic` ブロックは「1つのリソース内のネストされた設定ブロックを複数生成する」ために使います。たとえば複数の S3 バケットを作るなら `for_each`、1つのセキュリティグループに複数の ingress ルールを追加するなら `dynamic` を使います。両者は併用可能で、`for_each` で生成したリソースの内部でさらに `dynamic` を使うケースも一般的です。

**Q2. Terragrunt の generate ブロックで生成したファイルは Git 管理すべきですか？**

A. 基本的には管理しないことを推奨します。`generate` ブロックは `terragrunt.hcl` の内容から毎回再生成されるため、生成物をコミットすると「ソース（terragrunt.hcl）」と「生成物（.tf）」の二重管理になり、手動編集によるコンフリクトのリスクが生じます。`.gitignore` に `provider.tf` や `backend.tf` など生成対象ファイル名を追加し、CI/CD パイプラインで都度生成する運用が安全です。

**Q3. 動的生成を使うと terraform plan の可読性が落ちませんか？対策はありますか？**

A. 確かに `dynamic` ブロックや `for_each` を多用すると、HCL コード自体からは最終的な構成がイメージしづらくなります。対策としては、(1) `terraform plan -out=tfplan` の後に `terraform show -json tfplan` を使って実際の生成結果を可視化する、(2) 複雑な合成ロジックは `locals` に切り出してコメントではなく変数名で意図を表現する、(3) `variable` の `validation` ブロックで入力段階の不整合を早期検出する、といった運用を組み合わせることで可読性と保守性を両立できます。

## まとめ

Terraform における「generate」的な動的設定合成は、単一の機能ではなく、`dynamic` ブロック・`for_each`/`count`・Terragrunt の `generate` ブロック・CDKTF のコード生成といった複数のレイヤーで実現される設計思想です。state への影響や、AWS/GCP/Azure それぞれの特性を踏まえた上で、入力スキーマの明確化とモジュール分割を適切に行うことが、スケーラブルかつ保守性の高いインフラコードを書くための鍵となります。まずは `dynamic` ブロックによる小さな合成から始め、必要に応じて Terragrunt や CDKTF といったより強力な合成手段へステップアップしていくことをお勧めします。
