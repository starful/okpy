---
title: 'Terraform Provider Aliases で複数の AWS・Azure アカウントを単一構成で管理する実践ガイド'
date: 2026-10-20
category: terraform
slug: terraform-provider-aliases-managing-multiple-aws-and-azure-accounts-in-a-single-
summary: 'Terraform を使ったマルチアカウント・マルチリージョン構成では、1 つの `.tf` ファイルやモジュールの中で複数のクラウドアカウントを同時に操作したい場面が頻繁に発生します。たとえば「本番用 AWS アカウントと検証用 AWS アカウントの両方に同じリソースをデプロイしたい」「東京リージョンとシンガポ…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261020151114.jpg'
lang: ja
---

# Terraform Provider Aliases で複数の AWS・Azure アカウントを単一構成で管理する実践ガイド

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261020151114.jpg)


## はじめに

Terraform を使ったマルチアカウント・マルチリージョン構成では、1 つの `.tf` ファイルやモジュールの中で複数のクラウドアカウントを同時に操作したい場面が頻繁に発生します。たとえば「本番用 AWS アカウントと検証用 AWS アカウントの両方に同じリソースをデプロイしたい」「東京リージョンとシンガポールリージョンにまたがるネットワークを構築したい」といったケースです。こうした要件に応えるのが **Provider Aliases（プロバイダーエイリアス）** という仕組みです。本記事では Provider Aliases の基本概念から HCL 実装例、state への影響、モジュール設計、運用上の注意点までを体系的に解説します。

## Provider Aliases の概念

Terraform における `provider` ブロックは、どのクラウド・どの認証情報・どのリージョンに対してリソースを作成するかを定義するものです。通常、1 つの `provider "aws"` ブロックだけを定義すれば、そのプロバイダー設定がデフォルトとして全リソースに適用されます。

しかし、同一の `provider` 種別(たとえば `aws`)を複数の設定で使い分けたい場合、Terraform は `alias` 引数を使った複数プロバイダー定義をサポートしています。

```hcl
provider "aws" {
  region = "ap-northeast-1"
  alias  = "tokyo"
}

provider "aws" {
  region = "ap-southeast-1"
  alias  = "singapore"
}
```

この仕組みのポイントは次の通りです。

- `alias` を指定しないプロバイダー定義は「デフォルトプロバイダー」として扱われる
- `alias` を指定したプロバイダーは、リソースやモジュール側で明示的に `provider = aws.tokyo` のように参照しないと使われない
- 1 つの provider 種別につき、エイリアスの数に制限はない(実務上は管理のしやすさで数を絞るべき)

これにより、「同じプロバイダープラグインだが異なる接続先」を 1 つの Terraform 構成内で共存させることができます。

## 複数 AWS アカウントを扱う HCL 例

マルチアカウント構成でよくあるのは、IAM ロールの Assume Role を使って異なるアカウントに切り替えるパターンです。

```hcl
provider "aws" {
  region = "ap-northeast-1"
  alias  = "prod"

  assume_role {
    role_arn = "arn:aws:iam::111111111111:role/terraform-deploy"
  }
}

provider "aws" {
  region = "ap-northeast-1"
  alias  = "staging"

  assume_role {
    role_arn = "arn:aws:iam::222222222222:role/terraform-deploy"
  }
}

resource "aws_s3_bucket" "prod_bucket" {
  provider = aws.prod
  bucket   = "okpy-prod-assets"
}

resource "aws_s3_bucket" "staging_bucket" {
  provider = aws.staging
  bucket   = "okpy-staging-assets"
}
```

このように、同じ `aws_s3_bucket` リソースタイプでも `provider` 引数でどちらのアカウントに作るかを明示的に切り分けられます。これは Terraform の「1 つの構成で複数の実行対象を扱う」という設計思想を体現した典型例です。

## Azure との組み合わせ例

Azure でも同様にサブスクリプション単位でエイリアスを使い分けられます。

```hcl
provider "azurerm" {
  features {}
  alias           = "sub_a"
  subscription_id = "aaaaaaaa-0000-0000-0000-000000000001"
}

provider "azurerm" {
  features {}
  alias           = "sub_b"
  subscription_id = "bbbbbbbb-0000-0000-0000-000000000002"
}

resource "azurerm_resource_group" "rg_a" {
  provider = azurerm.sub_a
  name     = "okpy-rg-a"
  location = "Japan East"
}

resource "azurerm_resource_group" "rg_b" {
  provider = azurerm.sub_b
  name     = "okpy-rg-b"
  location = "Japan East"
}
```

AWS のアカウント概念と Azure のサブスクリプション概念は構造が異なりますが、Terraform の Provider Aliases を使う発想自体は共通しています。GCP の場合はプロジェクト単位でエイリアスを分けるのが一般的で、`provider "google" { alias = "project_a" project = "..." }` のように書きます。つまり、クラウドベンダーが異なっても「認証境界の単位ごとにプロバイダーを分離する」という考え方は AWS・Azure・GCP で共通しており、Provider Aliases はマルチクラウド・マルチアカウント戦略の中核的な技術要素だと言えます。

## state への影響

Provider Aliases を使う際に最も誤解されやすいのが「state ファイルの管理単位」です。重要な点を整理します。

1. **エイリアスの違いは state 上のリソースアドレスに直接現れない**
   `aws_s3_bucket.prod_bucket` と `aws_s3_bucket.staging_bucket` はリソース名で区別されており、`provider` 引数自体は state のメタデータとして記録されますが、リソースアドレスの一部にはなりません。つまり命名規則で混乱しないよう、リソース名に `prod` や `staging` を含めるなど明示的な設計が必要です。

2. **同一 state ファイル内に複数アカウントのリソースが混在する**
   デフォルトでは 1 つの state ファイルに、prod・staging 両方のリソース情報が記録されます。これは「1 つの state が壊れると複数アカウントに影響が及ぶ」というリスクを意味します。小規模な検証では許容できますが、本番運用では **state を分離し、アカウントごとに別の Terraform 構成(別ディレクトリ・別 backend)にする** 方が安全性は高まります。

3. **`terraform state mv` や `import` でも provider を意識する**
   既存リソースを import する場合、対象の provider エイリアスを明示しないと誤った認証情報でAPIコールが行われ、意図しないアカウントへの参照になってしまう可能性があります。

```hcl
terraform import -provider=aws.staging aws_s3_bucket.staging_bucket okpy-staging-assets
```

## モジュールでの Provider Aliases の受け渡し

モジュール内で複数プロバイダーを使う場合、**呼び出し元で明示的に `providers` ブロックを使ってマッピングする** 必要があります。Terraform 0.13 以降はこの方式が標準です。

```hcl
# modules/s3_bucket/main.tf
terraform {
  required_providers {
    aws = {
      source                = "hashicorp/aws"
      configuration_aliases = [aws.prod, aws.staging]
    }
  }
}

resource "aws_s3_bucket" "this" {
  provider = aws.prod
  bucket   = var.bucket_name
}
```

```hcl
# root module
module "bucket_prod" {
  source = "./modules/s3_bucket"
  providers = {
    aws.prod    = aws.prod
    aws.staging = aws.staging
  }
  bucket_name = "okpy-prod-assets"
}
```

ポイントは `configuration_aliases` を使ってモジュール内部で「このモジュールは複数の aws プロバイダーを要求する」と明示しておくことです。これを忘れると、モジュール呼び出し時にエイリアスの対応関係が曖昧になり、意図しないプロバイダーがデフォルトで使われてしまう危険があります。

## 注意点

Provider Aliases は強力な機能ですが、運用上は次のような落とし穴があります。

- **`for_each` や `count` と組み合わせられない**
  Provider の指定(`provider = aws.xxx`)は静的な値でなければならず、変数や式から動的に導出することはできません。「10個のアカウントをループで処理したい」というニーズには、素の Provider Aliases では対応できないため、`for_each` を使ったモジュール呼び出しと、事前に定義した複数プロバイダーの組み合わせで対処する必要があります。

- **プロバイダー定義の増加に伴う可読性の低下**
  アカウント数が増えるほど `provider` ブロックと `alias` の対応関係が複雑化します。アカウント数が多くなる場合は、Provider Aliases よりも **Terraform Workspace** や **ディレクトリ分割+別 state** の方が保守性に優れることが多いです。

- **デフォルトプロバイダーの意図しない利用**
  エイリアスを使っていても、モジュール内でうっかり `provider` 引数を省略すると、暗黙的にデフォルトプロバイダー(通常は本番用の最初の認証情報)が使われてしまうことがあります。特に `assume_role` を使う構成では、意図しないアカウントへのリソース作成という重大な事故に直結するため、CI 上で `terraform plan` の出力を必ず確認する運用ルールを設けるべきです。

- **認証情報のスコープ管理**
  各エイリアスに対応する IAM ロールやサブスクリプションの権限は最小権限の原則に従うべきです。1 つの Terraform 実行コンテキストに複数アカウントの認証情報が同時に存在するため、誤操作時の影響範囲(ブラストラディウス)が広がりやすい点は十分に認識しておく必要があります。

- **Terraform Cloud / Enterprise のワークスペース変数との相性**
  CI/CD パイプラインで環境変数として認証情報を注入する場合、エイリアスごとに異なる認証情報セットを明示的に渡す必要があり、単純な `AWS_PROFILE` 切り替えでは対応できないケースがあります。

## FAQ

**Q1. Provider Aliases と Terraform Workspace はどちらを使うべきですか?**
目的が異なります。Workspace は「同じ構成を複数の環境(dev/staging/prod)に使い分ける」ための仕組みで、通常は 1 つのアカウント・1 つのプロバイダー設定を前提としています。一方 Provider Aliases は「1 回の `terraform apply` の中で複数のアカウント・リージョンに同時にリソースを作成する」ための仕組みです。環境を切り替えるだけならWorkspace、1 構成で複数アカウントに同時展開したいならProvider Aliasesが適しています。両者を併用することも可能ですが、構成が複雑になりすぎないよう設計段階で慎重に検討してください。

**Q2. エイリアス名に命名規則はありますか?**
Terraform 自体には命名規則の制約はなく、英数字とアンダースコアが使える程度です。ただし実務上は、アカウントIDやリージョン名、用途が一目でわかる名前(`prod`, `staging`, `tokyo`, `singapore` など)を付けることを強く推奨します。チームで命名規則をドキュメント化しておくと、モジュールの `providers` マッピングを書く際の事故を減らせます。

**Q3. GCP でも同じようにマルチプロジェクト構成は組めますか?**
はい、可能です。GCP の `google` プロバイダーも `alias` と `project` 引数を組み合わせることで、複数のGCPプロジェクトを 1 つの構成内で扱えます。基本的な考え方は AWS のマルチアカウント、Azure のマルチサブスクリプションと同じで、「認証境界ごとにプロバイダーを分離し、リソースやモジュール呼び出し時に明示的に対応付ける」という設計パターンが共通しています。クラウドを問わずこのパターンを理解しておくと、マルチクラウド構成への応用もスムーズになります。

## まとめ

Provider Aliases は、単一の Terraform 構成内で複数のクラウドアカウント・サブスクリプション・リージョンを扱うための基本的かつ強力な機能です。HCL 上での定義自体はシンプルですが、state の管理、モジュールへの `providers` マッピング、`for_each` との非互換性など、実運用では注意すべき点が多く存在します。アカウント数が少ない場合はProvider Aliasesによる一元管理が効率的ですが、アカウント数が増えてきた場合は、state分離やディレクトリ構成の見直しも含めて、保守性とセキュリティのバランスを取った設計を検討することをお勧めします。
