---
title: 'Terraformによるマルチリージョンデプロイ戦略と実践パターン'
date: 2026-08-05
category: terraform
slug: terraform-multi-region-deployment-strategies-and-patterns
summary: 'グローバルにサービスを展開する場合、単一リージョンでの運用は可用性・レイテンシ・コンプライアンスの観点で限界があります。Terraformはクラウドリソースをコードとして宣言的に管理できるため、マルチリージョン構成の再現性と保守性を大きく高めます。本記事では、Terraformでマルチリージョンデプロイを設計・実…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260805161419.jpg'
lang: ja
---

# Terraformによるマルチリージョンデプロイ戦略と実践パターン

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260805161419.jpg)


## はじめに

グローバルにサービスを展開する場合、単一リージョンでの運用は可用性・レイテンシ・コンプライアンスの観点で限界があります。Terraformはクラウドリソースをコードとして宣言的に管理できるため、マルチリージョン構成の再現性と保守性を大きく高めます。本記事では、Terraformでマルチリージョンデプロイを設計・実装する際の基本概念、具体的なHCLコード例、stateの扱い方、モジュール設計、注意点、そしてよくある質問についてまとめます。

## マルチリージョン構成の基本概念

マルチリージョン構成には主に以下のパターンがあります。

1. **Active-Active構成**: 複数リージョンで同時にトラフィックを受け付け、負荷分散する構成。可用性とレイテンシの両方を最適化できますが、データ整合性の設計が複雑になります。
2. **Active-Passive構成**: メインリージョンで稼働し、障害時にセカンダリリージョンへフェイルオーバーする構成。ディザスタリカバリ(DR)目的で採用されることが多いです。
3. **地理分散(Geo-distribution)構成**: ユーザーの地理的位置に応じて最適なリージョンへルーティングする構成。CDNやGeoDNSと組み合わせることが一般的です。

Terraformでこれらを実現する際の核心は、**プロバイダーのエイリアス(alias)機能**と**モジュールの再利用**です。AWS、GCP、Azureいずれも「リージョン」という概念を持ちますが、リソースのスコープ(グローバル/リージョナル/ゾーナル)がプロバイダーごとに異なる点に注意が必要です。

## プロバイダーエイリアスによるマルチリージョン定義

Terraformでは、同一プロバイダーに対して複数のリージョンを扱うために`alias`を使います。

```hcl
provider "aws" {
  region = "ap-northeast-1"
  alias  = "tokyo"
}

provider "aws" {
  region = "us-east-1"
  alias  = "virginia"
}

resource "aws_instance" "app_tokyo" {
  provider      = aws.tokyo
  ami           = "ami-0abcd1234efgh5678"
  instance_type = "t3.medium"

  tags = {
    Name   = "app-server"
    Region = "tokyo"
  }
}

resource "aws_instance" "app_virginia" {
  provider      = aws.virginia
  ami           = "ami-0ijkl9012mnop3456"
  instance_type = "t3.medium"

  tags = {
    Name   = "app-server"
    Region = "virginia"
  }
}
```

GCPの場合はプロバイダーブロックの`region`と`zone`を切り替え、Azureの場合は`location`をリソース単位で指定するのが一般的です。GCPは`google`プロバイダーに対してもエイリアスを使えますが、Azureの`azurerm`プロバイダーはサブスクリプション単位が基本となるため、リージョンはリソースの`location`引数で制御する点がAWSと異なります。

```hcl
resource "azurerm_resource_group" "app_japan" {
  name     = "rg-app-japaneast"
  location = "Japan East"
}

resource "azurerm_resource_group" "app_europe" {
  name     = "rg-app-westeurope"
  location = "West Europe"
}
```

## モジュール設計によるリージョン展開の共通化

複数リージョンに同一構成を展開する場合、コードの重複を避けるためにモジュール化するのがベストプラクティスです。

```hcl
# modules/regional_stack/main.tf
variable "region" {
  type = string
}

variable "instance_count" {
  type    = number
  default = 2
}

resource "aws_vpc" "this" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "vpc-${var.region}"
  }
}

resource "aws_instance" "this" {
  count         = var.instance_count
  ami           = "ami-0abcd1234efgh5678"
  instance_type = "t3.medium"

  tags = {
    Name = "app-${var.region}-${count.index}"
  }
}
```

呼び出し側では、リージョンごとにプロバイダーを切り替えつつモジュールを複数回呼び出します。

```hcl
module "tokyo_stack" {
  source          = "./modules/regional_stack"
  providers       = { aws = aws.tokyo }
  region          = "ap-northeast-1"
  instance_count  = 3
}

module "virginia_stack" {
  source          = "./modules/regional_stack"
  providers       = { aws = aws.virginia }
  region          = "us-east-1"
  instance_count  = 2
}
```

このように`providers`ブロックでモジュールに使用するプロバイダーエイリアスを明示的に渡すことで、モジュール自体はリージョン非依存のまま再利用できます。

## Stateの管理戦略

マルチリージョン構成ではstateファイルの設計が特に重要になります。主な選択肢は以下の3つです。

### 1. 単一state・複数リージョン

全リージョンのリソースを1つのstateファイルで管理する方法です。小〜中規模構成ではシンプルですが、リージョン単位で部分的にapplyできない、stateファイルが肥大化する、といったデメリットがあります。

### 2. リージョンごとにstateを分割

`terraform_remote_state`やワークスペース、あるいはディレクトリ分割によってリージョンごとにstateを独立させる方法です。

```hcl
terraform {
  backend "s3" {
    bucket         = "okpy-terraform-state"
    key            = "app/tokyo/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

バックエンド自体のリージョンとデプロイ先リージョンは分離できますが、実務上は各リージョンのstateバケットをそのリージョン(または一貫したホームリージョン)に置き、`dynamodb_table`によるロックで同時実行の競合を防ぐのが定石です。GCSバックエンド(GCP)やAzure Storage Account(Azure)でも同様にロック機構を意識する必要があります。

### 3. Terraformワークスペースによる分離

```
terraform workspace new tokyo
terraform workspace new virginia
terraform workspace select tokyo
terraform apply
```

ワークスペースは同一バックエンド内で状態を論理的に分離しますが、リージョンごとにバックエンド設定(暗号化キーやアクセス制御)を変えたい場合には不向きです。実運用では**リージョンごとにディレクトリとstateファイルを分割する構成**が最も柔軟性が高く、多くのチームで採用されています。

## 依存関係とデータ共有

リージョン間でリソースを連携させる場合(例: グローバルロードバランサーがリージョナルなバックエンドを参照する)、`terraform_remote_state`データソースを使って他リージョンのstateを参照します。

```hcl
data "terraform_remote_state" "tokyo" {
  backend = "s3"
  config = {
    bucket = "okpy-terraform-state"
    key    = "app/tokyo/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

resource "aws_route53_record" "global" {
  zone_id = var.zone_id
  name    = "app.okpy.example.com"
  type    = "A"

  set_identifier = "tokyo"
  latency_routing_policy {
    region = "ap-northeast-1"
  }

  alias {
    name                   = data.terraform_remote_state.tokyo.outputs.alb_dns_name
    zone_id                = data.terraform_remote_state.tokyo.outputs.alb_zone_id
    evaluate_target_health = true
  }
}
```

GCPではCloud DNSのジオルーティングポリシー、AzureではTraffic ManagerやFront Doorが同様の役割を担い、いずれもTerraformプロバイダーからネイティブに設定可能です。

## 注意点

- **グローバルリソースの重複作成に注意**: IAMロールやRoute 53ホストゾーンなど、クラウドによってはグローバルスコープのリソースが存在します。リージョンごとにモジュールを回すと誤って重複作成してしまうことがあるため、グローバルリソースは専用のstate・モジュールに切り出すべきです。
- **APIレートリミットとapply時間**: リージョン数が増えるほど`terraform apply`の対象リソースも増え、レートリミットやタイムアウトに直面しやすくなります。`-parallelism`オプションの調整や、CI/CDでのリージョン別ジョブ分割が有効です。
- **プロバイダーバージョンの一貫性**: 複数リージョン・複数モジュールで異なるプロバイダーバージョンが混在すると、微妙な挙動差異が発生します。`required_providers`のバージョン制約をルートモジュールで統一管理しましょう。
- **DR訓練とドリフト検知**: Active-Passive構成のセカンダリリージョンは普段トラフィックを受けないため、実際のリソース状態と設定がずれていないか`terraform plan`によるドリフト検知を定期的に(CIのスケジュール実行などで)行うことが重要です。
- **コストの可視化**: リージョンをまたぐデータ転送(Cross-Region Data Transfer)は想定以上にコストがかさむことがあります。設計段階でトラフィックパターンを見積もっておきましょう。

## FAQ

**Q1. マルチリージョン構成では必ずstateをリージョンごとに分割すべきですか?**

小規模な構成やリソース数が少ない場合は単一stateでも運用可能ですが、リージョンが3つ以上になる、あるいはチームが分かれて作業する場合は分割を強く推奨します。分割することでapply範囲を限定でき、障害時の影響範囲も小さくできます。

**Q2. AWS・GCP・Azureを併用するマルチクラウド構成でも同じ考え方が使えますか?**

基本的な考え方(プロバイダーのエイリアス化、モジュールの再利用、state分割)は共通して使えます。ただし各クラウドでリソースのスコープやネットワークモデルが異なるため、共通モジュールで抽象化しすぎるとかえって複雑になりがちです。実務では「クラウドごとにモジュールを分け、上位のオーケストレーション層(CI/CDやTerragrunt等)でリージョン・クラウドの組み合わせを制御する」構成が扱いやすいです。

**Q3. リージョン追加時の作業を自動化するにはどうすればよいですか?**

リージョンごとの差分をvariables(tfvarsファイルなど)として外出しし、モジュール呼び出し自体はコードを変えずに新しいtfvarsファイルとバックエンド設定を追加するだけで済む構成にしておくと、新規リージョン追加はコピー&パラメータ変更だけで完結します。TerragruntやCI/CDのマトリクスビルドと組み合わせると、リージョン追加のPRレビューも容易になります。

## まとめ

Terraformによるマルチリージョンデプロイは、プロバイダーエイリアス・モジュール化・state分割という3つの柱を押さえることで、拡張性と保守性の高い構成を実現できます。AWS・GCP・Azureそれぞれのリージョンスコープの違いを理解した上で、グローバルリソースとリージョナルリソースを明確に分離し、CI/CDと組み合わせて運用することが、安定したマルチリージョン基盤構築の鍵となります。
