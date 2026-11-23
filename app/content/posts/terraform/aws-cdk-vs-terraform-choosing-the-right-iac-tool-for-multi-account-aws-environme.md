---
title: 'AWS CDK vs Terraform: マルチアカウントAWS環境に最適なIaCツールの選び方'
date: 2026-11-23
category: terraform
slug: aws-cdk-vs-terraform-choosing-the-right-iac-tool-for-multi-account-aws-environme
summary: 'マルチアカウントのAWS環境を運用する際、IaC（Infrastructure as Code）ツールの選定は長期的な保守性を左右する重要な意思決定です。本記事では AWS CDK と Terraform を、概念・コード例・state管理・モジュール設計・注意点という観点から比較し、実践的な選び方を解説します。…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261123193940.jpg'
lang: ja
---

# AWS CDK vs Terraform: マルチアカウントAWS環境に最適なIaCツールの選び方

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261123193940.jpg)


マルチアカウントのAWS環境を運用する際、IaC（Infrastructure as Code）ツールの選定は長期的な保守性を左右する重要な意思決定です。本記事では AWS CDK と Terraform を、概念・コード例・state管理・モジュール設計・注意点という観点から比較し、実践的な選び方を解説します。

## 1. 概念の整理

### AWS CDK とは

AWS CDK（Cloud Development Kit）は、TypeScript・Python・Java などの汎用プログラミング言語でAWSリソースを定義し、最終的にCloudFormationテンプレートへ合成（synth）するフレームワークです。プログラミング言語のループ・条件分岐・クラス継承をそのまま使えるため、複雑な条件付きリソース生成や再利用可能なConstruct（部品）を書きやすいのが特徴です。

### Terraform とは

Terraform はHashiCorp（現IBM傘下）が開発する宣言型IaCツールで、HCL（HashiCorp Configuration Language）という専用DSLでインフラを記述します。プロバイダーという抽象層を介して AWS・GCP・Azure・Kubernetes など多数のサービスを同一の文法で扱えるのが最大の特徴です。

### マルチアカウント設計における違い

- **CDK**: アカウントごとに `cdk bootstrap` を実行し、CloudFormationの実行ロール（`CloudFormationExecutionRole`）をアカウントに配置する必要があります。Stageという概念でアカウント・リージョンをまたいだパイプラインを組みやすい設計です。
- **Terraform**: `provider` ブロックの `alias` と `assume_role` を組み合わせることで、1つのコード内から複数アカウントのリソースを横断的に管理できます。AWS専用ではなくマルチクラウド前提の抽象化がされています。

## 2. Terraform HCL例：マルチアカウント構成

典型的な「管理アカウント + 複数ワークロードアカウント」構成をHCLで示します。

```hcl
# providers.tf
terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
  alias  = "management"
}

provider "aws" {
  region = "ap-northeast-1"
  alias  = "workload_prod"

  assume_role {
    role_arn     = "arn:aws:iam::222233334444:role/TerraformDeployRole"
    session_name = "terraform-prod"
  }
}

provider "aws" {
  region = "ap-northeast-1"
  alias  = "workload_stg"

  assume_role {
    role_arn     = "arn:aws:iam::333344445555:role/TerraformDeployRole"
    session_name = "terraform-stg"
  }
}
```

モジュール呼び出し側で `providers` を明示的に渡すことで、同じモジュール定義を複数アカウントに適用できます。

```hcl
module "vpc_prod" {
  source = "./modules/vpc"

  providers = {
    aws = aws.workload_prod
  }

  cidr_block  = "10.10.0.0/16"
  environment = "prod"
}

module "vpc_stg" {
  source = "./modules/vpc"

  providers = {
    aws = aws.workload_stg
  }

  cidr_block  = "10.20.0.0/16"
  environment = "stg"
}
```

この書き方のメリットは、1回の `terraform plan` で複数アカウントへの変更差分を一括確認できる点です。一方でCDKの場合は、CDK Pipelines や Stage クラスを使い、アカウントごとに別のCloudFormationスタックをデプロイするパイプライン設計が基本になります。

## 3. State管理の実務ポイント

Terraformの最大の運用課題はstateファイルの管理です。マルチアカウントでは以下の設計が定石です。

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "okpy-terraform-state"
    key            = "workload-prod/network/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}
```

- **state分離**: アカウント単位・レイヤー単位（network / iam / app）でstateファイルを分割し、1つのstateが肥大化して`plan`に時間がかかる状態を避けます。
- **ロック**: DynamoDBテーブルでstate lockを行い、同時applyによる競合破壊を防ぎます。Terraform 1.10以降ではS3ネイティブロックも選択肢です。
- **state自体の権限管理**: stateファイルにはシークレットが平文で残ることがあるため、S3バケットの暗号化とバケットポリシーでの最小権限アクセスが必須です。

一方CDK/CloudFormationは、AWSが管理するスタックの状態（CloudFormationのスタックイベント）がそのまま"state"として機能するため、state管理をユーザーが直接意識する必要はありません。これはCDKの運用上の大きな利点です。ただしドリフト検出の精度や柔軟性はTerraformの `terraform plan` に一日の長があります。

## 4. モジュール設計

### Terraformモジュール

```
modules/
  vpc/
    main.tf
    variables.tf
    outputs.tf
  iam-baseline/
    main.tf
    variables.tf
```

アカウント横断で使う「ベースラインモジュール」（Config、GuardDuty有効化、IAMパスワードポリシーなど）を1つ作り、各アカウント用のルートモジュールから `providers` を切り替えて呼び出す構成が一般的です。Terraform RegistryやGit参照（`source = "git::https://..."`）でバージョン管理することで、組織全体のガバナンスを一箇所に集約できます。

### CDK Construct

CDKでは同様の役割を「Construct」が担います。L2/L3 Constructをnpmパッケージとして社内配布し、各チームのスタックにimportして使う設計が主流です。プログラミング言語のクラス継承・インターフェースが使えるため、「このConstructを継承すれば必須のタグ付けが強制される」といった設計がしやすい反面、学習コストはHCLより高めです。

## 5. 注意点

- **IAM権限の設計**: Terraformのassume_roleパターンでは、実行主体（CI/CDのロール）が全ワークロードアカウントのロールをAssumeできる強力な権限を持つため、権限境界（Permission Boundary）とSCPでの制御が欠かせません。
- **CDK bootstrap忘れ**: 新規アカウントに`cdk bootstrap`をし忘れるとデプロイが失敗します。アカウント追加時の自動化（Control Tower連携など）に組み込むのが安全です。
- **ドリフト**: 手動コンソール操作によるドリフトは両ツール共通のリスクです。Terraformは`terraform plan`で、CDKは`cfn drift-detection`で定期検知する運用を組み込みましょう。
- **シークレット管理**: TerraformのstateにAPIキー等が残留しないよう、SecretsManagerやSSM Parameter StoreのARN参照に留め、値そのものをコードやstateに書かないことが重要です。
- **並行運用時の二重管理**: CDKとTerraformを同一リソースに対して併用すると、どちらが"真実の情報源（Source of Truth）"か曖昧になり事故の元になります。リソース単位・アカウント単位で管理ツールを明確に分離しましょう。

## 6. AWS/GCP/Azureとの関係

Terraformはプロバイダーを切り替えるだけでAWS・GCP・Azureを同一の文法で扱えるため、マルチクラウド戦略を取る組織や、将来的なクラウド移行の柔軟性を重視する場合に有利です。HashiCorpはTerraform CDK（CDKTF）も提供しており、TypeScript等でTerraformを書くことも可能ですが、エコシステムの成熟度ではネイティブHCLが依然優勢です。

一方AWS CDKはAWS専業です。GCPにはGoogle自身が提供するものはなく、Pulumiのような第三者ツールが近い立ち位置を占めます。AzureにはBicepという類似のネイティブIaCがあります。したがって「将来GCP・Azureへの展開可能性がある」場合はTerraformが無難な選択、「AWS専業でプログラミング言語の表現力を活かしたい」場合はCDKが適しています。

## FAQ

**Q1. 既存のTerraform環境にCDKを後から混在させても問題ないですか？**
A. アカウント単位・リソース種別単位で管理範囲を明確に分ければ技術的には可能です。ただし同一リソースを両方で管理するとstateとCloudFormationスタックの不整合が発生するため、移行期は対象リソースをタグ等で明示的に区分管理することを推奨します。

**Q2. マルチアカウントでTerraformのstateファイルはアカウントごとに分けるべきですか？**
A. 基本的には分けるべきです。アカウント単位・レイヤー単位（ネットワーク/IAM/アプリ）で分割することで、`plan`実行時間の短縮、影響範囲の局所化、誤ってPROD環境に変更を適用するリスクの低減につながります。

**Q3. CDKのStageとTerraformのworkspaceは同じ用途で使えますか？**
A. 用途は似ていますが性質が異なります。CDKのStageはアカウント・リージョンをまたいだデプロイ対象の集合を表すのに対し、Terraformのworkspaceは同一バックエンド内でstateを論理的に分離する仕組みです。アカウント分離が目的ならworkspaceよりも別々のbackend設定（stateファイル自体を分ける）の方が安全性が高く、実務ではこちらが推奨されます。

## まとめ

AWS CDKとTerraformはどちらも成熟したIaCツールであり、優劣ではなく「組織のクラウド戦略」と「チームのスキルセット」に応じた選択が重要です。AWS専業でプログラミング言語の表現力を重視するならCDK、マルチクラウド前提やHCLの宣言的シンプルさを重視するならTerraformが適しています。いずれを選ぶ場合も、マルチアカウント環境ではstateおよびスタックの分離設計とIAM権限の最小化を最優先で設計することが、事故のない運用への近道です。
