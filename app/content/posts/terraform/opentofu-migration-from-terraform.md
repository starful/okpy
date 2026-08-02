---
category: terraform
cover: https://storage.googleapis.com/ok-project-assets/okpy/2026072521491300.jpg
date: 2026-07-22
lang: ja
slug: opentofu-migration-from-terraform
summary: HashiCorp社によるTerraformのライセンス変更（BSL/BUSLへの移行）を受けて、オープンソースのコミュニティ主導によるフォークプロジェクト「OpenTofu」が誕生しました。Linux
  Foundationのもとで管理されるOpenTofuは、Terraformの完全なオープンソース代替品として…
title: OpenTofu移行実践ガイド：Terraformからの完全移行手順と運用・コード互換性
---

# OpenTofu移行実践ガイド：Terraformからの完全移行手順と運用・コード互換性

![cover](https://storage.googleapis.com/ok-project-assets/okpy/2026072521491300.jpg)


HashiCorp社によるTerraformのライセンス変更（BSL/BUSLへの移行）を受けて、オープンソースのコミュニティ主導によるフォークプロジェクト「OpenTofu」が誕生しました。Linux Foundationのもとで管理されるOpenTofuは、Terraformの完全なオープンソース代替品として急速に普及を進めています。

本記事では、OKPy編集部が既存のTerraform環境からOpenTofuへスムーズに移行するための実践的なガイドをお届けします。概念の整理からHCL互換性、State（ステートファイル）の移行、モジュール運用、主要クラウドプロバイダー（AWS / GCP / Azure）との関係、そして注意点やFAQまで、現場のDevOps/SREエンジニアが必要とする情報を網羅的に解説します。

---

## 1. OpenTofuの基本概念と移行の背景

### 1.1 OpenTofuとは何か？

OpenTofuは、HashiCorp Terraformのバージョン 1.5.7 をベースにフォークされた、オープンソース（MPL 2.0ライセンス）のInfrastructure as Code（IaC）ツールです。Linux Foundationの傘下で中立的に開発・運用されており、特定のベンダーロックインを回避しながら、オープンソースエコシステムの中で継続的に進化を続けています。

### 1.2 フォークの背景とライセンス問題

2023年8月、HashiCorpはTerraformを含む自社製品のライセンスを「Mozilla Public License 2.0 (MPL 2.0)」から「Business Source License v1.1 (BSL/BUSL)」へ改定しました。これにより、Terraformと競合する商用サービスを提供する事業者は、特定の制約を受けることになりました。

この改定を受けて、コミュニティや競合他社、オープンソース推進団体が立ち上がり、「OpenTofu（初期名称: OpenTF）」が発足しました。OpenTofuは誰でも自由に無償で利用・改変・商用利用ができる純粋なオープンソースツールとしての地位を確立しています。

### 1.3 Terraformとの互換性（Drop-in Replacement）

OpenTofuは、Terraform v1.5.x までの完全な下位互換性（ドロップイン置換性）を維持するように設計されています。既存のHCL（HashiCorp Configuration Language）コード、ステートファイル、Terraform Provider、Terraform Moduleは、最小限の手間でそのままOpenTofuへ移行可能です。

### 1.4 主要クラウド（AWS / GCP / Azure）との関係

OpenTofuは、主要なクラウドプロバイダー（AWS, GCP, Microsoft Azureなど）のIaCプロバイダーと完全な互換性を保持しています。

- **AWS Provider (`hashicorp/aws`)**
- **Google Cloud Provider (`hashicorp/google`)**
- **Azure Provider (`hashicorp/azurerm`)**

これらのプロバイダーは、OpenTofu環境下でも問題なく読み込み・実行が可能です。AWS Identity and Access Management (IAM) のロール引き受け、GCPのWorkload Identity、AzureのService PrincipalやManaged Identityを利用した認証・認可の仕組みも、従来通り機能します。クラウド事業者側のAPIや運用方式に変更を迫られることはありません。

---

## 2. HCLコードの互換性とOpenTofuにおける実行例

### 2.1 既存のHCLコードの互換性

Terraform 1.5.7 以前で記述された `.tf` ファイルは、OpenTofuでも変更なしでそのまま実行できます。構文エラーや型システムの差異を心配する必要は基本的にありません。

### 2.2 基本的なHCLコードの実行例

以下は、AWS上にVPCとS3バケットを作成する一般的なHCLコードの例です。Terraformで利用していた構成ファイルをそのまま使用します。

```hcl
# main.tf

terraform {
  required_version = ">= 1.6.0" # OpenTofuのバージョンを指定可能

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "okpy-opentofu-vpc"
    Environment = "production"
    ManagedBy   = "OpenTofu"
  }
}

resource "aws_s3_bucket" "log_bucket" {
  bucket        = "okpy-app-logs-2024-production"
  force_destroy = false

  tags = {
    Name        = "okpy-log-bucket"
    Environment = "production"
  }
}

output "vpc_id" {
  description = "作成されたVPCのID"
  value       = aws_vpc.main.id
}
```

コマンドラインインターフェース（CLI）もTerraformとほぼ同一です。`terraform` コマンドを `tofu` コマンドに置き換えるだけで機能します。

```bash
# 初期化
tofu init

# 計画の確認
tofu plan

# リソースの適用
tofu apply
```

### 2.3 OpenTofu独自の拡張機能（State Encryptionなど）

OpenTofuはTerraformとの互換性を保ちつつも、コミュニティの要望に基づいた新機能を独自に導入しています。代表例が **State Encryption（ステートファイルのネイティブ暗号化）** です。

従来のTerraformでは、Stateファイル内に平文で保存されるセンシティブなデータ（パスワードやAPIキー）の取り扱いが課題でした。OpenTofu v1.7.0 以降では、HCL内で暗号化設定をネイティブに記述できるようになっています。

```hcl
# main.tf (OpenTofu v1.7+ の独自機能例)

terraform {
  encryption {
    method "aes_gcm" "passphrase" {
      keys = provider::aws::secret_key # 例: 外部鍵管理の利用
    }

    state {
      method   = method.aes_gcm.passphrase
      enforced = true
    }
  }
}
```

このように、OpenTofuは単純なクローンにとどまらず、セキュリティや機能性の向上を独自に進めています。

---

## 3. ステートファイル（State）の移行とバックエンド設定

### 3.1 ステートファイルの互換性ルール

TerraformからOpenTofuへの移行で最も重要なのが、**ステートファイル（`terraform.tfstate`）のバージョン互換性** です。

1. **Terraform v1.5.7 以前からの移行**:
   完全な完全互換性があります。何特別な変換処理を行わずに、そのままOpenTofuで読み込みが可能です。
2. **Terraform v1.6.x 〜 v1.7.x からの移行**:
   Terraform v1.6以降でStateフォーマットに変更が加えられていない範囲であれば、基本的に移行可能です。ただし、Terraform v1.7以降で導入された特定の独自機能（Terraform testの高度な機能など）を使用している場合、Stateの非互換が発生することがあります。
3. **安全な移行の原則**:
   移行作業を行う直前に、必ず既存Stateファイルのバックアップを取得してください。

### 3.2 移行のステップ・バイ・ステップ手順

以下に、ローカル環境またはバックエンドに保存されたStateを安全にOpenTofuへ移行する手順を示します。

#### ステップ1: CLIのインストール
各種パッケージマネージャー（Homebrew, apt, dnfなど）を使って `tofu` CLIをインストールします。

```bash
# macOS (Homebrew) の場合
brew install opentofu

# Linux (Debian/Ubuntu) の場合
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://get.opentofu.org/opentofu.gpg | sudo tee /etc/apt/keyrings/opentofu.gpg > /dev/null
curl -fsSL https://packages.opentofu.org/opentofu/tofu/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/opentofu.gpg
echo "deb [signed-by=/etc/apt/keyrings/opentofu.gpg] https://packages.opentofu.org/opentofu/tofu/any/ any main" | sudo tee /etc/apt/sources.list.d/opentofu.list
sudo apt-get update
sudo apt-get install -y tofu
```

#### ステップ2: 現行Stateのバックアップ
Terraformコマンドを使用して、現在のStateを確実にローカルへ保存します。

```bash
terraform state pull > backup_before_migration.tfstate
```

#### ステップ3: OpenTofuによる初期化
移行対象のディレクトリへ移動し、`tofu init` を実行します。

```bash
tofu init
```

この操作により、`.terraform` ディレクトリのプロバイダープラグインやモジュールがOpenTofu用の構造で再取得されます。既存の `.terraform` ディレクトリや `.terraform.lock.hcl` を事前に削除・再生成しておくと、より確実です。

```bash
rm -rf .terraform
tofu init
```

#### ステップ4: 差分確認（Plan）
コードと実際のインフラ、Stateの間に予期せぬ差分が発生していないか確認します。

```bash
tofu plan
```

「`No changes. Your infrastructure matches the configuration.`」と表示されれば、移行は成功です。

---

### 3.3 クラウドバックエンドの設定（AWS / GCP / Azure）

OpenTofuは、主要クラウドのバックエンド（Remote State Storage）に対応しています。設定構文はTerraformと完全に同一です。

#### AWS S3 バックエンド例

```hcl
terraform {
  backend "s3" {
    bucket         = "okpy-tfstate-bucket"
    key            = "production/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "okpy-tfstate-locks"
    encrypt        = true
  }
}
```

#### GCP GCS バックエンド例

```hcl
terraform {
  backend "gcs" {
    bucket      = "okpy-tfstate-gcs-bucket"
    prefix      = "production/state"
  }
}
```

#### Azure Blob Storage バックエンド例

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "sttfstateokpy"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}
```

### 3.4 移行時のロールバック戦略

万が一、OpenTofuでの `tofu apply` 実行時に問題が発生した場合に備え、以下のロールバック手順を準備しておきます。

1. **Stateの復元**: バックアップしておいた `backup_before_migration.tfstate` をリモートバックエンドに書き戻します。
   ```bash
   terraform state push backup_before_migration.tfstate
   ```
2. **実行バイナリの書き戻し**: CI/CDパイプラインや運用スクリプトの実行コマンドを `tofu` から `terraform` へ戻します。

---

## 4. モジュールの利用とレジストリの移行

### 4.1 既存Terraformモジュールの互換性

パブリックなTerraform RegistryやGitHub等で公開されているサードパーティ製モジュール（例: AWS公式の `terraform-aws-modules/vpc/aws` など）は、OpenTofuでもそのまま利用可能です。

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"

  name = "okpy-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["ap-northeast-1a", "ap-northeast-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
}
```

### 4.2 OpenTofu Registryの仕組み

OpenTofuプロジェクトは、HashiCorp社の利用規約に制限されずにプロバイダーやモジュールを提供できるよう、独自の概念である **OpenTofu Registry**（`registry.opentofu.org`）を運用しています。

`tofu init` を実行すると、OpenTofuは自動的にOpenTofu Registryへ接続します。OpenTofu Registryは、従来のHashiCorp Registry上に存在するオープンソースのプロバイダーやモジュールをインデックス化・ミラーリングしているため、ユーザーが明示的に `source` の URL や記述を書き換える必要はありません。

### 4.3 プライベートモジュールの取り扱い

Gitリポジトリ（GitHub, GitLab, Bitbucketなど）を直接指定しているモジュールソースや、プライベートGitリポジトリを参照している場合は、一切の変更なしで読み込むことができます。

```hcl
# Gitリポジトリ参照（変更不要）
module "my_custom_service" {
  source = "git::https://github.com/okpy-org/terraform-modules.git//app?ref=v1.2.0"
  
  environment = "production"
}
```

---

## 5. 移行における注意点と運用上のリスク

OpenTofuへの移行は技術的にスムーズに行えるケースが多いですが、長期的な運用においては以下の点に注意する必要があります。

### 5.1 ライセンス面の違い

- **Terraform**: Business Source License (BSL 1.1)。競合製品の提供や再配布において商用ライセンス違反となるリスクがある。
- **OpenTofu**: Mozilla Public License 2.0 (MPL 2.0)。商用利用、改変、再配布、自社サービスへの組み込みが自由に許可されている。

自社のビジネスモデルがTerraformのBSL条項に抵触する可能性がある場合は、OpenTofuへの移行が強い推奨事項となります。

### 5.2 将来的な機能の乖離（Divergence）

OpenTofu v1.6 / v1.7 以降、独自機能（State暗号化、改善されたループ構文など）の開発が進んでいます。一方で、HashiCorp社が提供するTerraform v1.6 / v1.7 / v1.8 以降の独自機能や新構文は、OpenTofuには取り込まれません。

将来的に両者の機能差が広がると、以下のリスクが生じます。

- **相互運用性の喪失**: OpenTofu独自のHCL構文を使用したコードは、将来的にTerraformで実行できなくなります。
- **モジュールの互換性**: サードパーティ製モジュールがTerraform専用の最新構文に依存した場合、OpenTofuで動かなくなる可能性があります（逆も同様）。

### 5.3 CI/CDパイプラインの変更

GitHub Actions、GitLab CI、CircleCI、Jenkins等でIaCの自動化を行っている場合、パイプラインのステップを更新する必要があります。

#### GitHub Actions の例

既存の `hashicorp/setup-terraform` アクションの代わりに、OpenTofu公式のアクション `opentofu/setup-opentofu` を導入します。

```yaml
name: "OpenTofu Deployment"

on:
  push:
    branches:
      - main

jobs:
  opentofu:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup OpenTofu
        uses: opentofu/setup-opentofu@v1
        with:
          tofu_version: "1.7.0"

      - name: OpenTofu Init
        run: tofu init

      - name: OpenTofu Plan
        run: tofu plan

      - name: OpenTofu Apply
        if: github.ref == 'refs/heads/main'
        run: tofu apply -auto-approve
```

### 5.4 プロバイダーエコシステムのサポート状況

現在、主要プロバイダー（AWS, Google, Azure, Cloudflare, Datadog等）はオープンソースライセンスの下で公開されており、OpenTofu Registry経由で正常に利用可能です。しかし、将来的に一部のベンダーがHashiCorp社専用のプロバイダー仕様に変更を加えるリスクがゼロではないため、利用している重要プロバイダーの追従状況を定期的に監視することをお勧めします。

---

## 6. よくある質問（FAQ）

### FAQ 1: Terraform v1.6以降を使っている場合でも、OpenTofuへ直ちに移行できますか？

**回答**: 
原則として可能です。ただし、Terraform v1.6やv1.7以降で追加されたHashiCorp独自のState機能や新構文（`test` ブロックの特定拡張など）を利用している場合、互換性チェックが必要です。
移行前に必ず `tofu plan` をローカルまたは検証環境で実行し、Stateや構成ファイルのパースエラーが発生しないかテストしてください。通常のリソース定義（AWS/GCP/Azure等の標準的なIaC記述）であれば、問題なく移行できます。

### FAQ 2: AWS, GCP, Azureの公式プロバイダーはOpenTofuでもそのまま更新・利用し続けられますか？

**回答**: 
はい、利用し続けられます。
AWS, GCP, Azure等の主要クラウドプロバイダーはMPL 2.0などのオープンソースライセンスで個別のリポジトリとして公開されており、OpenTofu Registry（`registry.opentofu.org`）を通じて最新版が透過的に取得されます。AWS IAMロール認証やGCP Workload Identityなどの高度な認証方式も含め、問題なく動作します。

### FAQ 3: OpenTofuへ移行した後、万が一Terraformに戻す（ロールバックする）ことは可能ですか？

**回答**: 
OpenTofu独自の機能（例: State暗号化機能やOpenTofu v1.7+ の新構文）を使用していない限り、Terraformへ戻すことは可能です。
ただし、一度OpenTofuで `tofu apply` を実行してStateファイルの内部フォーマットバージョンが更新された場合、古いバージョンのTerraformではStateを読み込めなくなるリスクがあります。このリスクを回避するために、移行作業時のStateのバックアップ取得と、移行直後はOpenTofu独自機能の利用を一時的に控える運用を推奨します。

---

## 7. まとめ

OpenTofuは、Terraformが培ってきた豊富なエコシステムやHCLの知識をそのまま活かしつつ、オープンソースの透明性と持続可能性を担保するための最適な選択肢です。

- **高い互換性**: 既存の `.tf` コードや主要クラウド（AWS / GCP / Azure）のプロバイダー、S3/GCS等のバックエンドをそのまま活用可能。
- **簡単な移行**: `terraform` コマンドを `tofu` コマンドに切り替えるだけのドロップイン置換が可能。
- **独自の進化**: State暗号化をはじめとするセキュリティ強化や機能改善がコミュニティ主導で活発に進行中。

ライセンスリスクを回避し、長期的かつ安全なインフラ自動化基盤を構築するために、本ガイドを参考にOpenTofuへの移行を検討してみてください。

---
*本記事は「OKPy」編集部によって執筆・検証されました。*
