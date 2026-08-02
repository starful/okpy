---
title: 'Terraform Secrets Management with HashiCorp Vault 実践ガイド'
date: 2026-07-30
category: terraform
slug: terraform-secrets-management-with-hashicorp-vault
summary: 'Terraform でインフラを構築する際、データベースのパスワード、API キー、TLS 証明書などの機密情報(シークレット)をどのように扱うかは非常に重要な設計課題です。シークレットを `.tf` ファイルや `terraform.tfstate` にそのまま平文で書き込んでしまうと、Git リポジトリや s…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260730135632.jpg'
lang: ja
---

# Terraform Secrets Management with HashiCorp Vault 実践ガイド

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260730135632.jpg)


## はじめに

Terraform でインフラを構築する際、データベースのパスワード、API キー、TLS 証明書などの機密情報(シークレット)をどのように扱うかは非常に重要な設計課題です。シークレットを `.tf` ファイルや `terraform.tfstate` にそのまま平文で書き込んでしまうと、Git リポジトリや state ファイルの漏洩がそのままセキュリティインシデントに直結します。

HashiCorp Vault は、シークレットの一元管理・動的発行・暗号化・監査ログを提供するツールであり、Terraform と組み合わせることで「シークレットをコードに書かない」運用を実現できます。本記事では、概念整理から実際の HCL コード例、state の扱い、モジュール化、運用上の注意点までを一気通貫で解説します。

## 1. 基本概念

### 1.1 Vault が解決する課題

Terraform だけでインフラを管理していると、以下のような問題に直面します。

- シークレットを変数として渡すと `terraform.tfstate` に平文で保存される
- CI/CD パイプラインの環境変数にシークレットを埋め込むと漏洩リスクが高まる
- シークレットのローテーション(定期更新)を手動で行う必要がある
- 誰がいつどのシークレットにアクセスしたかの監査が困難

Vault はこれらを以下の仕組みで解決します。

| 機能 | 説明 |
|---|---|
| Static Secrets Engine (KV) | key-value 形式でシークレットを保管・バージョン管理 |
| Dynamic Secrets Engine | AWS/GCP/Azure/DB の認証情報をリクエスト時に動的発行し、TTL 後に自動失効 |
| Transit Engine | アプリケーション側でシークレットを保持せず暗号化・復号を Vault に委譲 |
| Auth Methods | AppRole, Kubernetes, AWS IAM など多様な認証方式でアクセス制御 |
| Audit Log | すべてのシークレットアクセスを記録し監査証跡を残す |

### 1.2 Terraform との連携方式

Terraform から Vault を利用する方法は主に2つあります。

1. **Terraform Provider for Vault**: `hashicorp/vault` プロバイダーを使い、Vault 自体のポリシーやシークレットエンジンを Terraform で構成管理する(Vault を Terraform で「構築する」側)
2. **Vault からシークレットを取得して他リソースに注入**: `vault_generic_secret` や `vault_kv_secret_v2` データソースで Vault からシークレットを読み取り、RDS のパスワードや Kubernetes Secret に流し込む(Vault を Terraform が「利用する」側)

多くの実務では両方を組み合わせ、Vault のセットアップ自体も Terraform で IaC 化しつつ、実際のワークロードのシークレット取得も Terraform 経由で行います。

## 2. HCL 実装例

### 2.1 Provider 設定

```hcl
terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 4.0"
    }
  }
}

provider "vault" {
  address = "https://vault.internal.example.com:8200"
  # トークンは環境変数 VAULT_TOKEN で渡し、HCL には書かない
}
```

トークンや認証情報を `provider` ブロックにハードコードしないことが鉄則です。実運用では環境変数 `VAULT_TOKEN` や、後述する AppRole 認証を利用します。

### 2.2 KV シークレットエンジンの有効化とポリシー定義

```hcl
resource "vault_mount" "kv" {
  path        = "secret"
  type        = "kv-v2"
  description = "アプリケーション用シークレットストア"
}

resource "vault_policy" "app_read" {
  name = "app-read-policy"

  policy = <<-EOT
    path "secret/data/app/*" {
      capabilities = ["read"]
    }
  EOT
}
```

### 2.3 AppRole 認証の設定(CI/CD からのアクセス用)

```hcl
resource "vault_auth_backend" "approle" {
  type = "approle"
}

resource "vault_approle_auth_backend_role" "ci" {
  backend        = vault_auth_backend.approle.path
  role_name      = "ci-pipeline"
  token_policies = [vault_policy.app_read.name]
  token_ttl      = 3600
  token_max_ttl  = 7200
}
```

CI/CD パイプラインは AppRole の `role_id` と `secret_id` を使って Vault にログインし、短命トークンを取得してからシークレットを読み取ります。長期間有効な root トークンをパイプラインに埋め込むのは避けるべきアンチパターンです。

### 2.4 シークレットの書き込みと参照

```hcl
resource "vault_kv_secret_v2" "db_creds" {
  mount = vault_mount.kv.path
  name  = "app/database"

  data_json = jsonencode({
    username = "app_user"
    password = random_password.db.result
  })
}

resource "random_password" "db" {
  length  = 24
  special = true
}
```

シークレットの値そのものを `variable` として外部から渡すのではなく、`random_password` で Terraform 内に生成し Vault に格納する構成にすると、シークレットが tfvars ファイルや CLI 引数として露出する経路をなくせます。

### 2.5 動的シークレットの活用(AWS 認証情報の例)

```hcl
resource "vault_aws_secret_backend" "aws" {
  path       = "aws"
  access_key = var.vault_admin_access_key
  secret_key = var.vault_admin_secret_key
}

resource "vault_aws_secret_backend_role" "ec2_readonly" {
  backend         = vault_aws_secret_backend.aws.path
  name            = "ec2-readonly"
  credential_type = "iam_user"

  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ec2:Describe*"]
      Resource = "*"
    }]
  })
}

data "vault_aws_access_credentials" "creds" {
  backend = vault_aws_secret_backend.aws.path
  role    = vault_aws_secret_backend_role.ec2_readonly.name
  type    = "creds"
}
```

`data.vault_aws_access_credentials` はリクエストのたびに Vault が新しい IAM ユーザーの一時認証情報を発行し、TTL 経過後に自動失効します。長期間有効な IAM アクセスキーを手動発行・配布する必要がなくなり、漏洩時の被害範囲を最小化できます。

## 3. State ファイルの扱い

### 3.1 なぜ state が危険なのか

Terraform は `apply` 時に取得したすべての値(データソースの出力を含む)を `terraform.tfstate` に平文で記録します。上記の `vault_kv_secret_v2` や `vault_aws_access_credentials` の結果も例外ではなく、**state ファイル自体がシークレットの塊になる**という事実を理解する必要があります。

対策は以下の通りです。

1. **リモートバックエンドの暗号化**: S3 + DynamoDB(ロック用)や Terraform Cloud を使い、S3 バケット側でサーバーサイド暗号化(SSE-KMS)を必須化する
2. **state へのアクセス制御**: IAM ポリシーや Terraform Cloud のワークスペース権限で state 読み取りを最小権限化する
3. **短命トークンの利用**: 動的シークレットは TTL が短いため、state に残っても失効後は無害化される
4. **`sensitive = true` の付与**: output やリソース属性に `sensitive` フラグを付け、CLI 出力やログへの表示を防ぐ(ただし state 内の平文保存自体は防げない点に注意)

```hcl
terraform {
  backend "s3" {
    bucket         = "okpy-terraform-state"
    key            = "vault/terraform.tfstate"
    region         = "ap-northeast-1"
    encrypt        = true
    kms_key_id     = "alias/terraform-state-key"
    dynamodb_table = "terraform-lock"
  }
}

output "db_password" {
  value     = random_password.db.result
  sensitive = true
}
```

### 3.2 state を汚さない設計パターン

もっとも安全なのは「Terraform に極力シークレットの実値を持たせない」設計です。具体的には、Terraform では Vault 側にシークレットを書き込む・ポリシーを構成するところまでを担当し、アプリケーションの実行時に Vault Agent や External Secrets Operator(Kubernetes)経由で直接シークレットを取得させる方式が推奨されます。これにより Terraform の state にはシークレットの「保管場所」だけが記録され、値そのものは記録されません。

## 4. モジュール構成

複数環境(dev/stg/prod)や複数チームでの再利用を考えると、Vault 関連リソースはモジュール化しておくと保守性が上がります。

```
modules/
  vault-app-secrets/
    main.tf
    variables.tf
    outputs.tf
environments/
  dev/
    main.tf
  prod/
    main.tf
```

```hcl
# modules/vault-app-secrets/main.tf
variable "app_name" {
  type = string
}

variable "policies" {
  type    = list(string)
  default = []
}

resource "vault_mount" "kv" {
  path = "secret/${var.app_name}"
  type = "kv-v2"
}

resource "vault_policy" "this" {
  name   = "${var.app_name}-policy"
  policy = file("${path.module}/policies/${var.app_name}.hcl")
}

output "mount_path" {
  value = vault_mount.kv.path
}
```

```hcl
# environments/prod/main.tf
module "vault_app_secrets" {
  source   = "../../modules/vault-app-secrets"
  app_name = "billing-service"
}
```

環境ごとにポリシーファイルを分離し、モジュールの引数(`app_name` など)だけを変えることで、dev/stg/prod 間の設定ドリフトを防ぎます。また、モジュールの `outputs.tf` では Vault のパスやロール名のみを返し、シークレットの値そのものを output しないようにするのが安全な設計です。

## 5. 注意点・アンチパターン

- **root トークンの常用禁止**: CI/CD やアプリケーションからのアクセスには必ず AppRole や Kubernetes Auth など、スコープが限定された認証方式を使う
- **Terraform Cloud/Enterprise の Sentinel や OPA でポリシーチェック**: Vault リソースの変更(ポリシー緩和など)を人手のレビューだけに頼らず、ポリシーエンジンで自動検査する
- **`terraform plan` の出力にも注意**: `sensitive` 指定がないとシークレットが plan の diff にそのまま表示されることがある
- **Vault 自体の高可用性**: Vault が単一障害点になると `terraform apply` 自体が失敗するため、Vault クラスタの Raft ストレージや Auto-Unseal(KMS 連携)を構成し可用性を確保する
- **シークレットのローテーション運用**: 動的シークレットの TTL を短く設定しすぎるとアプリケーションの再接続処理が頻発する。ワークロードの特性に応じて TTL を調整する
- **CI 実行環境の一時トークン漏洩**: GitHub Actions などのログにトークンが出力されないよう `::add-mask::` 相当のマスキング設定を併用する

## 6. パブリッククラウドとの関係

Vault はクラウドベンダー非依存のツールですが、AWS/GCP/Azure それぞれのネイティブなシークレット管理サービスとも比較・併用が検討されます。

- **AWS**: Vault の AWS Secrets Engine は IAM の一時認証情報を動的発行できる点で AWS Secrets Manager や IAM Roles Anywhere と競合しますが、マルチクラウド構成では Vault を単一の管理面として使うメリットがあります。Terraform の `aws` プロバイダーと `vault` プロバイダーを併用し、Vault で発行した一時認証情報を `aws` プロバイダーの `assume_role` や `access_key`/`secret_key` に渡す構成も可能です。
- **GCP**: Vault の GCP Secrets Engine は Service Account の一時キーを動的発行できます。GCP Secret Manager との使い分けとしては、単一クラウドで完結するなら Secret Manager、マルチクラウドや動的認証情報の発行が必要なら Vault、という判断軸が一般的です。
- **Azure**: Vault の Azure Secrets Engine は Azure AD のサービスプリンシパルを動的発行します。Azure Key Vault と機能が重複しますが、Vault は Azure/AWS/GCP をまたいだシークレット管理を一元化できる点が差別化要素です。

すでに単一クラウドに閉じた構成であれば、まずはクラウドネイティブのシークレット管理(AWS Secrets Manager、GCP Secret Manager、Azure Key Vault)の採用を検討し、マルチクラウド・オンプレ混在・動的シークレット発行が必要になった段階で Vault の導入を検討するのが現実的な進め方です。

## 7. FAQ

**Q1. Vault を使わずに Terraform の `sensitive` 変数だけでシークレットを守れますか?**

`sensitive = true` は CLI 出力やログでの表示を抑制するだけで、`terraform.tfstate` への平文保存自体は防げません。state の暗号化・アクセス制御と併用しても、シークレットのローテーションや監査ログといった Vault が提供する機能は代替できないため、恒久的な対策としては不十分です。

**Q2. Vault provider のバージョンアップで注意すべき点は何ですか?**

`hashicorp/vault` プロバイダーは v3 から v4 への移行でリソース名やスキーマが変更された箇所があります(例: `vault_generic_secret` から `vault_kv_secret_v2` への移行が推奨されています)。バージョンを固定せずに `required_providers` を運用していると、意図しないメジャーアップデートで `apply` が破壊的変更を起こす可能性があるため、`~> 4.0` のようにメジャーバージョンを固定した上で、変更履歴(CHANGELOG)を確認してから計画的にアップグレードすることを推奨します。

**Q3. Terraform の実行環境(CI/CD)にはどうやって Vault の認証情報を渡すのが安全ですか?**

長期間有効な Vault トークンを CI/CD の環境変数に直接埋め込むのは避け、AppRole 認証で `role_id` と `secret_id` を分離して渡す、あるいは Kubernetes 上で実行するなら Kubernetes Auth Method を使い Pod の ServiceAccount トークンで Vault にログインする方式が推奨されます。特に GitHub Actions では OIDC 連携を使い、Vault 側で GitHub の OIDC トークンを検証する JWT Auth Method を構成すると、静的なシークレットを一切パイプラインに保存せずに済みます。

## まとめ

Terraform と HashiCorp Vault を組み合わせることで、シークレットをコードや state から可能な限り分離し、動的発行・自動失効・監査可能な運用へと移行できます。重要なのは「Vault を導入すれば安全」という単純な話ではなく、state の暗号化、認証方式の選定、モジュール設計、TTL のチューニングといった複数のレイヤーを組み合わせて初めて堅牢な仕組みになるという点です。既存の AWS/GCP/Azure ネイティブなシークレット管理サービスとの使い分けも含め、自社のクラウド構成と運用体制に合った落としどころを見極めながら段階的に導入することをおすすめします。
