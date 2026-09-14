---
title: 'Terraformパフォーマンス最適化と大規模デプロイメント実践ガイド'
date: 2026-09-14
category: terraform
slug: terraform-performance-optimization-and-large-scale-deployments
summary: 'Terraformはインフラをコードで管理するデファクトスタンダードのツールですが、管理対象リソースが数百、数千規模に増えると`plan`や`apply`の実行時間が急激に悪化し、stateファイルの肥大化やチーム間のコンフリクトなど、小規模環境では顕在化しなかった問題が次々と表面化します。本記事では、Terra…'
lang: ja
---

# Terraformパフォーマンス最適化と大規模デプロイメント実践ガイド

## はじめに

Terraformはインフラをコードで管理するデファクトスタンダードのツールですが、管理対象リソースが数百、数千規模に増えると`plan`や`apply`の実行時間が急激に悪化し、stateファイルの肥大化やチーム間のコンフリクトなど、小規模環境では顕在化しなかった問題が次々と表面化します。本記事では、Terraformを大規模環境で運用する際に直面するパフォーマンス上の課題と、その解決策を体系的に整理します。AWS・GCP・Azureいずれのクラウドでも共通する考え方を中心に、具体的なHCLサンプルとともに解説します。

## 大規模運用で起こりがちな問題

Terraformのパフォーマンス劣化は主に以下の要因から生じます。

- **単一stateファイルへのリソース集約**：数百リソースを1つのstateで管理すると、`plan`実行時に全リソースのリフレッシュ処理が走り、数分〜数十分かかるようになります。
- **モジュールの過度なネスト**：モジュールを何層にも重ねると、依存関係グラフの解決コストが増大します。
- **プロバイダAPIのレートリミット**：AWSやGCPのAPIは呼び出し回数に制限があり、並列度を上げすぎるとスロットリングでエラーになります。
- **不要なdata sourceの多用**：`data`ブロックは毎回APIを叩くため、大量に使うとplan時間に直結します。

これらを踏まえ、次章以降で具体的な対策を見ていきます。

## 1. stateファイルの分割戦略

最も効果が大きいのが**stateの分割**です。1つの巨大なstateにすべてのリソースを詰め込むのではなく、機能単位・環境単位・チーム単位でstateを分けることで、`plan`の対象リソース数を減らし、実行時間を大幅に短縮できます。

### 分割の考え方

- **環境ごと**（dev / staging / prod）
- **レイヤーごと**（ネットワーク基盤 / データベース / アプリケーション）
- **チームの責任範囲ごと**（プラットフォームチーム / プロダクトチーム）

```hcl
# backend.tf (network/ ディレクトリ)
terraform {
  backend "s3" {
    bucket         = "okpy-tfstate"
    key            = "network/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

```hcl
# backend.tf (app/ ディレクトリ)
terraform {
  backend "s3" {
    bucket         = "okpy-tfstate"
    key            = "app/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

state間で値を共有する場合は`terraform_remote_state`データソースを使います。

```hcl
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "okpy-tfstate"
    key    = "network/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

resource "aws_instance" "app" {
  subnet_id = data.terraform_remote_state.network.outputs.private_subnet_id
  # ...
}
```

state分割のトレードオフとして、リソース間の暗黙的な依存関係が見えにくくなる点には注意が必要です。分割単位は「変更頻度」と「所有者」が揃う境界を選ぶのがコツです。

## 2. モジュール設計のベストプラクティス

モジュールは再利用性を高める一方で、設計を誤るとplan時間の増大やコードの見通しの悪化を招きます。

### フラットなモジュール構成を心がける

過度なネスト（モジュールの中でモジュールを呼び、さらにその中で…という構造）は依存関係グラフを複雑にします。ルートモジュールから1〜2階層程度に抑えるのが目安です。

```hcl
module "vpc" {
  source = "./modules/vpc"

  cidr_block = "10.0.0.0/16"
  azs        = ["ap-northeast-1a", "ap-northeast-1c"]
}

module "eks_cluster" {
  source = "./modules/eks"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
}
```

### `for_each`を活用してリソース定義を集約

同種のリソースを大量に作る場合、`count`より`for_each`の方が安全です。`count`はインデックスに依存するため、リストの途中要素を削除すると他のリソースが再作成される危険があります。

```hcl
variable "buckets" {
  type = map(object({
    versioning = bool
  }))
}

resource "aws_s3_bucket" "this" {
  for_each = var.buckets
  bucket   = "okpy-${each.key}"
}

resource "aws_s3_bucket_versioning" "this" {
  for_each = { for k, v in var.buckets : k => v if v.versioning }
  bucket   = aws_s3_bucket.this[each.key].id

  versioning_configuration {
    status = "Enabled"
  }
}
```

### モジュールのバージョン固定

Terraform Registryやgitリポジトリからモジュールを読み込む場合は、バージョンを必ず固定します。固定しないとCI環境ごとに異なるバージョンが取得され、意図しない差分が発生します。

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"
  # ...
}
```

## 3. plan/applyの並列度とタイムアウト調整

Terraformはデフォルトで最大10個のリソースを並列に処理します(`-parallelism`)。大規模環境ではこの値がボトルネックにも、逆にAPIスロットリングの原因にもなり得ます。

```bash
# 並列度を上げてplan/apply時間を短縮(APIレートリミットに注意)
terraform apply -parallelism=30

# プロバイダ側のレートリミットが厳しい場合は逆に下げる
terraform apply -parallelism=5
```

プロバイダブロックでリトライ設定を明示的に行うことで、スロットリングによる一時的なエラーを吸収できます。

```hcl
provider "aws" {
  region = "ap-northeast-1"

  retry_mode  = "adaptive"
  max_retries = 25
}
```

GCPやAzureのプロバイダにも同様のリトライ・タイムアウト設定があります。GCPプロバイダでは`request_timeout`、Azureプロバイダでは各リソースブロック内の`timeouts`ブロックで調整可能です。

```hcl
resource "azurerm_kubernetes_cluster" "this" {
  # ...
  timeouts {
    create = "60m"
    update = "60m"
    delete = "30m"
  }
}
```

## 4. `-target`と部分applyの使い所

大規模state全体のplanに時間がかかる場合、緊急対応として`-target`オプションで特定リソースのみを対象にできます。ただし、これは恒常的な運用手段ではなく、あくまで一時的な回避策として使うべきです。依存関係グラフの一部だけを評価するため、他リソースとの整合性が崩れるリスクがあります。

```bash
terraform apply -target=module.app.aws_ecs_service.main
```

恒常的な解決策は前述のstate分割です。`-target`を日常的に使わざるを得ない状況は、state分割の見直しシグナルと捉えましょう。

## 5. `data`ソースの削減とキャッシュ戦略

`data`ブロックはリフレッシュのたびにAPI呼び出しが発生します。同じ情報を何度も参照する場合は、値をローカル変数やoutputに一度だけ格納し、再利用する設計に変えるとplan時間を削減できます。

```hcl
# 悪い例: 複数箇所で同じdata sourceを呼び出す
data "aws_ami" "latest" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# 良い例: ルートで一度だけ解決し、モジュールにはoutputとして渡す
module "app" {
  source = "./modules/app"
  ami_id = data.aws_ami.latest.id
}
```

## 6. state操作コマンドの活用

大規模stateの運用では、`terraform state`サブコマンドの理解が欠かせません。

```bash
# リソースの一覧を確認(全体planより高速)
terraform state list

# 特定リソースだけの情報を取得
terraform state show aws_instance.app

# リソースをstate間で移動(分割時に有用)
terraform state mv aws_instance.app module.app.aws_instance.main

# 誤ってインポートされたリソースを削除(実体は削除しない)
terraform state rm aws_instance.orphan
```

`terraform import`や`state mv`は、既存のリソースをTerraform管理下に移す際やstateを再編成する際に頻出します。大規模移行では`terraform plan -generate-config-out`(Terraform 1.5以降)を使うと、既存リソースからHCLコードを自動生成でき、手作業を大幅に削減できます。

## 7. CI/CDでの実行時間短縮

CIパイプラインでは、変更のあったディレクトリのみを対象にplan/applyを実行する仕組みが有効です。GitHub Actionsを例にすると、`paths`フィルタやworking-directoryのマトリクス化で実現できます。

```yaml
jobs:
  terraform:
    strategy:
      matrix:
        stack: [network, database, app]
    steps:
      - uses: actions/checkout@v4
      - name: Terraform Plan
        working-directory: ./environments/${{ matrix.stack }}
        run: terraform plan -out=tfplan
```

加えて、プロバイダプラグインのダウンロードをCIキャッシュに含めることで、`terraform init`の時間を短縮できます。

```yaml
      - uses: actions/cache@v4
        with:
          path: |
            .terraform
            .terraform.lock.hcl
          key: terraform-${{ hashFiles('**/.terraform.lock.hcl') }}
```

## クラウドプロバイダごとの留意点

- **AWS**：APIレートリミットはサービスごとに異なり、特にIAMやRoute53は制限が厳しめです。`aws_iam_role`などを大量に`for_each`で生成する場合は並列度を抑えるか、リトライ設定を強めに設定します。
- **GCP**：プロジェクト単位でAPIクォータが管理されるため、複数プロジェクトにまたがる大規模構成ではstateをプロジェクト単位で分割するのが自然です。
- **Azure**：リソースグループ単位での操作が基本となるため、stateもリソースグループ境界に合わせて分割すると、権限管理(RBAC)とも整合しやすくなります。

いずれのクラウドでも共通するのは、「APIの制限単位」と「state・モジュールの分割単位」を一致させることが、パフォーマンスと運用性の両立につながるという点です。

## 注意点・アンチパターン

- **巨大な単一stateの放置**：後から分割しようとすると`state mv`の作業量が膨大になります。プロジェクト初期から分割方針を決めておくのが得策です。
- **`count`の乱用によるリソース再作成事故**：リストの順序変更で無関係なリソースが削除・再作成されることがあります。`for_each`をデフォルトの選択肢にしましょう。
- **ロックファイルの不整合**：`.terraform.lock.hcl`をコミットし忘れると、CIとローカルでプロバイダバージョンがずれ、予期しない差分が発生します。
- **リモートバックエンドのロック未設定**：DynamoDBやCloud Storageのロック機構を設定しないと、複数人が同時にapplyしてstateが破損するリスクがあります。
- **secretsの平文管理**：state自体に機密情報が平文で残ることがあるため、暗号化(`encrypt = true`)とアクセス制御を必ず設定してください。

## FAQ

**Q1. planの実行時間が長すぎます。まず何を確認すべきですか？**
A. まず`terraform state list`でリソース数を確認してください。数百を超えている場合はstate分割が最優先の対策です。次に`data`ブロックの数と、不要なリフレッシュが発生していないかを確認します。`-refresh=false`で一時的に切り分けるのも診断に有効です。

**Q2. state分割後、リソース間の依存関係はどう管理すればよいですか？**
A. `terraform_remote_state`データソースでoutputを参照するのが基本パターンです。ただし依存が複雑になりすぎる場合は、Terraform CloudやSpacelift、Atlantisなどのオーケストレーションツールでstack間の実行順序を管理する方法も検討してください。

**Q3. `-target`を使わずに大規模applyの影響範囲を絞る方法はありますか？**
A. state分割に加えて、`terraform plan`の差分を確認してから`apply`するワークフローを徹底することが基本です。またTerraform 1.6以降の`-exclude`オプションを使うと、特定リソースを除外した形でplan/applyを実行でき、`-target`より安全に部分適用ができます。

## まとめ

大規模なTerraform運用におけるパフォーマンス最適化の本質は、「stateとモジュールの境界を、変更頻度・所有者・APIレートリミットの単位に合わせて設計する」ことに尽きます。`for_each`の活用やモジュールのバージョン固定といった基本的なプラクティスを徹底しつつ、CI/CDパイプラインでの並列実行や差分検出を組み合わせることで、リソース数が増えても実用的な実行時間を維持できます。まずは現在のstateリソース数と`plan`実行時間を計測し、ボトルネックを特定するところから始めてみてください。
