---
title: 'Terraform クロススタック参照とデータソースパターン実践ガイド'
date: 2026-08-02
category: terraform
slug: terraform-cross-stack-references-and-data-source-patterns
summary: 'Terraform で本番環境を運用していると、単一の Terraform 設定（ステート）だけで完結することは稀です。ネットワーク、IAM、データベース、アプリケーションといったレイヤーごとにステートを分割し、それぞれを独立してデプロイ・変更したいというニーズが必ず出てきます。このとき問題になるのが「あるステー…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260802150058.jpg'
lang: ja
---

# Terraform クロススタック参照とデータソースパターン実践ガイド

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260802150058.jpg)


## はじめに

Terraform で本番環境を運用していると、単一の Terraform 設定（ステート）だけで完結することは稀です。ネットワーク、IAM、データベース、アプリケーションといったレイヤーごとにステートを分割し、それぞれを独立してデプロイ・変更したいというニーズが必ず出てきます。このとき問題になるのが「あるステートで作成したリソースの情報を、別のステートからどう参照するか」です。これがいわゆる「クロススタック参照（cross-stack references）」であり、その中心的な実装手段が **データソース（data source）** です。

本ガイドでは、概念整理から具体的な HCL コード例、ステート設計、モジュール化、注意点、そして AWS / GCP / Azure における違いまでを一通り解説します。

## 1. クロススタック参照とは何か

クロススタック参照とは、複数の Terraform ステート（＝複数の `terraform apply` 単位）の間で、リソース情報をやり取りする仕組みの総称です。代表的な実現方法は次の3つです。

1. **リモートステートの参照**（`terraform_remote_state` データソース）
2. **データソースによる実リソースの検索**（例: `aws_vpc`、`google_compute_network` など）
3. **パラメータストアやタグを介した間接参照**（SSM Parameter Store、GCP のラベル、Azure のタグなど）

それぞれ得意・不得意があり、状況に応じて使い分けるのが実践上のポイントです。

### なぜステートを分割するのか

- **変更の影響範囲を小さくする**：ネットワークとアプリケーションを同一ステートにすると、アプリのデプロイのたびにネットワーク全体の diff が走り、事故のリスクが上がります。
- **チーム境界に合わせる**：インフラチームがネットワーク層を、開発チームがアプリ層を管理するような組織構造に対応できます。
- **apply 時間の短縮**：ステートが大きいほど plan/apply に時間がかかり、ロック競合も起きやすくなります。

一方で、分割すればするほど「どこで何を参照しているか」が見えにくくなるため、クロススタック参照の設計品質が運用の安定性を大きく左右します。

## 2. `terraform_remote_state` による参照

もっとも直接的な方法は、他のステートの `output` を `terraform_remote_state` データソースで読み込むことです。

```hcl
# network スタック側の output
output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}
```

```hcl
# app スタック側で network の state を参照
data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = "okpy-terraform-state"
    key    = "network/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

resource "aws_instance" "app" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
  subnet_id     = data.terraform_remote_state.network.outputs.private_subnet_ids[0]
}
```

この方式のメリットは、**参照先の output さえ安定していれば実装の変更に強い**ことです。デメリットは、参照元ステートの `outputs` ブロックがそのまま「公開 API」になるため、破壊的変更（output の削除・型変更）が下流の複数ステートに波及する点です。

## 3. データソースによる実リソース検索

`terraform_remote_state` はバックエンドへの直接アクセス権限が必要になるため、権限分離が厳しい環境では使いにくいことがあります。代替として、クラウド側の実リソースをタグや名前で検索するデータソースパターンがよく使われます。

```hcl
data "aws_vpc" "main" {
  tags = {
    Name        = "okpy-main-vpc"
    Environment = "production"
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }

  tags = {
    Tier = "private"
  }
}

resource "aws_instance" "app" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
  subnet_id     = data.aws_subnets.private.ids[0]
}
```

この方式は **バックエンドへのアクセス権限が不要**で、ステート同士が疎結合になる点が最大の利点です。反面、タグ設計が甘いと検索条件がヒットしない・複数ヒットしてしまうといった曖昧さが生じやすく、`terraform plan` の再現性がタグの一貫性に依存してしまいます。命名規則とタグ付けルールをチーム内で厳格に統一しておくことが前提条件になります。

## 4. パラメータストア／SSM を介した間接参照

もう一段疎結合にしたい場合、AWS Systems Manager Parameter Store や、GCP の Secret Manager、Azure の App Configuration を「連携用の掲示板」として使うパターンもあります。

```hcl
# network スタック側で書き込む
resource "aws_ssm_parameter" "vpc_id" {
  name  = "/okpy/network/vpc_id"
  type  = "String"
  value = aws_vpc.main.id
}
```

```hcl
# app スタック側で読み取る
data "aws_ssm_parameter" "vpc_id" {
  name = "/okpy/network/vpc_id"
}

resource "aws_security_group" "app" {
  vpc_id = data.aws_ssm_parameter.vpc_id.value
}
```

この方式はステートファイルへの直接アクセス権限が不要で、かつタグ検索よりも明示的・確定的です。ただし、値を書き込むステートと読み込むステートで **apply の順序依存** が生じるため、CI/CD パイプライン側で実行順序を制御する必要があります。

## 5. ステート設計の考え方

クロススタック参照の設計は、ステート分割の粒度と密接に関わります。一般的な指針は以下の通りです。

- **変更頻度でレイヤーを分ける**：ネットワークや IAM のように変更頻度が低いものと、アプリケーションのように頻繁にデプロイされるものは別ステートにする。
- **依存の方向を一方向に保つ**：`network → data → app` のように参照方向を一方向に統一し、循環参照（app が network を参照し、network も app の情報を参照するような構成）を避ける。
- **output は最小限かつ安定的に設計する**：内部実装の詳細（例えば個々のリソース名）をそのまま output せず、「他ステートが本当に必要とする値」だけを絞って公開する。
- **バックエンド設定を一元管理する**：S3 バケット名やキーのパスをハードコードで各所に埋め込むと、リネーム時に全ステートを修正する羽目になるため、`backend.tf` のパスは命名規則（例: `<env>/<layer>/terraform.tfstate`）として文書化しておく。

## 6. モジュールとの関係

データソースとクロススタック参照はモジュール設計とも密接に関わります。よくある誤解として「モジュール化すればステート分割も自動的にうまくいく」というものがありますが、これは別の話です。

- **モジュール**は同一ステート内でのコードの再利用単位（`module "network" { source = "./modules/network" }`）。
- **クロススタック参照**は異なるステート間でのデータのやり取り。

実践的には、各レイヤー（ネットワーク、IAM、アプリなど）をそれぞれ独立したルートモジュール（＝独立したステート）とし、その内部で共通モジュールを呼び出す構成がよく使われます。

```hcl
# network スタックのルート
module "vpc" {
  source   = "./modules/vpc"
  cidr_block = "10.0.0.0/16"
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
```

こうすることで、`module` によるコード再利用と `terraform_remote_state`／データソースによるステート間連携を明確に分離でき、責務がわかりやすくなります。共通モジュールをリファクタリングしても、output のインターフェースさえ壊さなければ下流ステートへの影響を抑えられます。

## 7. 注意点

- **循環依存を作らない**：A スタックが B の output を参照し、B も A の情報を必要とする設計は、原理的に解決できません。共通の依存関係は、より下位の共通スタック（例: `foundation`）に切り出しましょう。
- **`terraform_remote_state` の権限管理**：この方式は参照元ステートファイル全体（機密情報を含む可能性がある）への読み取り権限を要求します。IAM ポリシーで最小権限に絞り、可能ならタグ検索や SSM 経由の方式に切り替えることを検討してください。
- **データソースの非決定性**：`aws_subnets` のようにフィルタで複数件ヒットする可能性があるデータソースは、`plan` のたびに結果が変わりうるため、`ids[0]` のような添字アクセスは避け、`for_each` やソートで明示的に選択するほうが安全です。
- **apply 順序の暗黙依存**：クロススタック参照は「参照先が先に apply されている」ことを前提にします。CI/CD では `network → app` のようなパイプライン順序を明示的に定義し、依存関係をコードだけでなく運用フローとしても管理してください。
- **output のバージョニング**：output のキー名や型を変更する際は、下流スタックへの影響を事前に洗い出す。可能であれば新しいキーを追加してから旧キーを削除する「二段階移行」を行うと安全です。
- **ステートロックの競合**：複数人が同時に依存関係のあるステートを apply すると、ロック待ちや中途半端な状態での参照が発生しえます。CI 側で直列実行を保証する仕組み（例: 排他ロック付きパイプライン）を用意しましょう。

## 8. AWS / GCP / Azure における違い

基本的な考え方（`terraform_remote_state`、データソース検索、パラメータストア経由）はクラウドを問わず共通ですが、実装の細部には差があります。

- **AWS**：`terraform_remote_state` の backend に S3 + DynamoDB（ロック用）を使うのが定番。データソース検索はタグベース（`aws_vpc`、`aws_subnets` など）が充実しており、SSM Parameter Store を使った間接参照との相性も良い。
- **GCP**：バックエンドには GCS バケットが使われ、ロックは GCS のオブジェクトロックで自動的に扱われる。データソース検索はラベル（`google_compute_network` など）で行うが、AWS ほどタグベースのフィルタ機能が豊富ではないため、命名規則による検索（`name = "..."`）が中心になりやすい。
- **Azure**：バックエンドは Azure Storage Account（Blob）を使用し、ロックも自動管理される。リソースグループ単位でのデータソース検索（`azurerm_resource_group`、`azurerm_virtual_network` など）が基本パターンで、タグ検索よりも命名・リソースグループ構造に依存する設計が主流。

いずれのクラウドでも共通しているのは、「バックエンドへの直接アクセスを要する `terraform_remote_state` か、クラウド API 経由で疎結合に検索するデータソースか」というトレードオフです。マルチクラウドや権限分離が厳しい組織では、データソース検索やパラメータストア経由の方式を優先することをおすすめします。

## FAQ

**Q1. `terraform_remote_state` とデータソース検索、どちらを使うべきですか？**

小規模なチームで単一クラウド・単一 AWS アカウント内であれば `terraform_remote_state` はシンプルで扱いやすい選択です。一方、複数チーム・複数アカウントにまたがる場合や、ステートファイルへのアクセス権限を絞りたい場合は、タグベースのデータソース検索や SSM Parameter Store 経由の方式のほうが安全です。多くの現場では両者を併用し、「同一チーム内は remote_state、チーム境界をまたぐ場合はデータソース検索」という使い分けをしています。

**Q2. データソースの結果が `plan` のたびに変わってしまいます。どうすればよいですか？**

多くの場合、フィルタ条件が緩すぎて複数のリソースにマッチしていることが原因です。タグや名前をより一意になるよう設計し直すのが根本対策です。どうしても複数件になりうる場合は、`sort()` 関数で結果を安定した順序に整えてから選択する、あるいは `for_each` で全件を明示的に扱う設計に変更してください。

**Q3. モジュールを共通化すればステート分割は不要になりますか？**

いいえ、別の問題です。モジュールはコードの再利用単位であり、ステートは実行・権限・変更頻度の分離単位です。共通モジュールを使っていても、それぞれのステートで `terraform apply` を個別に実行する構成であれば、クロススタック参照の設計は依然として必要です。逆に、モジュールを共有していなくても、output のインターフェースさえ合わせればクロススタック参照は成立します。
