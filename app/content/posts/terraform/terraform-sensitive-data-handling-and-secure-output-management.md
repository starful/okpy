---
title: 'Terraform における機密情報の扱いとセキュアな Output 管理'
date: 2026-08-01
category: terraform
slug: terraform-sensitive-data-handling-and-secure-output-management
summary: 'Terraform でインフラをコード化していく中で、必ず直面するのが「パスワード」「APIキー」「証明書の秘密鍵」といった機密情報（センシティブデータ）の扱いです。うっかり `terraform plan` の実行ログや `terraform show` の出力に平文パスワードが表示されてしまい、CI のログに…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260801100457.jpg'
lang: ja
---

# Terraform における機密情報の扱いとセキュアな Output 管理

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260801100457.jpg)


Terraform でインフラをコード化していく中で、必ず直面するのが「パスワード」「APIキー」「証明書の秘密鍵」といった機密情報（センシティブデータ）の扱いです。うっかり `terraform plan` の実行ログや `terraform show` の出力に平文パスワードが表示されてしまい、CI のログに残ってしまった——という事故は珍しくありません。本記事では、Terraform が提供する `sensitive` 機能の仕組みから、state ファイルにおける機密情報の扱い、モジュール設計上の注意点、AWS/GCP/Azure のシークレット管理サービスとの連携までを実践的に解説します。

## 1. なぜ Terraform で機密情報の扱いが難しいのか

Terraform はリソースの作成・変更・削除を行うたびに、変数や属性の値を CLI 出力（plan/apply のログ）に表示します。これは差分を人間が確認できるようにするための設計ですが、裏を返せば「パスワードや秘密鍵もそのままログに出力されてしまう」ということです。

さらに厄介なのは、Terraform の **state ファイル**（`terraform.tfstate`）です。state には管理対象リソースの属性値がほぼすべて平文で保存されます。DB のマスターパスワードや TLS 秘密鍵をリソース引数として渡した場合、それらは state 内に文字列としてそのまま記録されます。つまり、`sensitive` 属性の指定は「CLI 出力を隠す」ためのものであり、「state を暗号化する」ためのものではないという点を最初に理解しておく必要があります。

## 2. `sensitive` 引数の基本

### 2.1 変数を sensitive にする

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}
```

`sensitive = true` を指定すると、`terraform plan`/`apply` の実行時にその変数を参照する箇所が `(sensitive value)` としてマスクされます。

```
  # aws_db_instance.main will be updated in-place
  ~ password = (sensitive value)
```

### 2.2 output を sensitive にする

output もセンシティブとして扱うことができます。

```hcl
output "db_password" {
  value     = random_password.db.result
  sensitive = true
}
```

`sensitive = true` を付けない output に機密情報を渡そうとすると、Terraform 0.14 以降ではエラーになります（伝播チェック）。これは「センシティブな値がうっかり非センシティブな output に漏れる」ことを防ぐ仕組みです。

### 2.3 リソース属性から派生した値の伝播

ある値がセンシティブな変数やリソース属性から計算された場合、その派生値も自動的にセンシティブ扱いになります。

```hcl
resource "random_password" "db" {
  length  = 16
  special = true
}

locals {
  connection_string = "postgres://admin:${random_password.db.result}@${aws_db_instance.main.endpoint}/app"
}
```

この `local.connection_string` は `random_password.db.result` を含むため、自動的にセンシティブとして扱われ、参照先で明示的に output しようとするとエラーになります。

## 3. HCL での実践例：RDS パスワードのハンドリング

AWS RDS を例に、パスワードをコード内にハードコードせず安全に扱う典型パターンを示します。

```hcl
resource "random_password" "db_master" {
  length           = 20
  special          = true
  override_special = "_%@"
}

resource "aws_secretsmanager_secret" "db_master" {
  name = "app/db/master-password"
}

resource "aws_secretsmanager_secret_version" "db_master" {
  secret_id     = aws_secretsmanager_secret.db_master.id
  secret_string = random_password.db_master.result
}

resource "aws_db_instance" "main" {
  identifier     = "app-db"
  engine         = "postgres"
  instance_class = "db.t3.medium"
  username       = "admin"
  password       = random_password.db_master.result

  manage_master_user_password = false # Secrets Manager 自動管理を使う場合は true にして password を省略
}
```

`aws_db_instance` には `manage_master_user_password = true` を指定すると、RDS 側が Secrets Manager にパスワードを自動生成・保存してくれるため、Terraform コード上にパスワードを一切書かずに済みます。これは 2022 年以降 AWS プロバイダーでサポートされた機能で、可能な限りこちらを優先すべきです。

```hcl
resource "aws_db_instance" "main" {
  identifier                  = "app-db"
  engine                      = "postgres"
  instance_class               = "db.t3.medium"
  username                     = "admin"
  manage_master_user_password  = true
}
```

## 4. state ファイルのセキュリティ

前述の通り `sensitive` はあくまで CLI 出力のマスクであり、state 自体は保護してくれません。state を安全に扱うための基本方針は以下の通りです。

- **リモートバックエンドの暗号化を有効にする**：S3 バックエンドなら SSE-KMS、GCS バックエンドなら CMEK、Azure Storage なら Storage Service Encryption を有効化します。
- **state へのアクセスを最小権限で制限する**：IAM ポリシーや Cloud IAM で、state を読めるユーザー・サービスを限定します。
- **state のロックを有効にする**：DynamoDB（AWS）や GCS のネイティブロックなど、同時書き込みによる破損を防ぎます。
- **state をバージョン管理・監査ログ対象にする**：誰がいつ state を読んだかを追跡できるようにします。

```hcl
terraform {
  backend "s3" {
    bucket         = "my-org-terraform-state"
    key            = "prod/network/terraform.tfstate"
    region         = "ap-northeast-1"
    encrypt        = true
    kms_key_id     = "alias/terraform-state-key"
    dynamodb_table = "terraform-locks"
  }
}
```

また、state をローカルに `terraform.tfstate` として残さないことも重要です。CI パイプラインでローカルバックエンドを使ってしまうと、機密情報がビルドアーティファクトやログに混入するリスクが高まります。

## 5. モジュール設計における注意点

モジュール化を進める際、機密情報の扱いには以下のような落とし穴があります。

1. **モジュール内部の output を sensitive にし忘れる**：子モジュールが `sensitive = true` を指定していても、それを呼び出す親モジュール側で再度 output する際に `sensitive = true` を付け忘れると、そこで露出してしまうことがあります（バージョンによって挙動が異なるため、必ず両方に明示すること）。

```hcl
# child module
output "api_key" {
  value     = aws_iam_access_key.app.secret
  sensitive = true
}

# root module
module "app" {
  source = "./modules/app"
}

output "app_api_key" {
  value     = module.app.api_key
  sensitive = true # 親側でも明示が必要
}
```

2. **入力変数のデフォルト値に機密情報を書かない**：`variable` の `default` にダミーであってもパスワードらしき文字列を書くと、レビュー時やドキュメント生成時に誤って本番値がコミットされるリスクを生みます。

3. **`for_each`/`count` のキーにセンシティブ値を使わない**：Terraform は `sensitive` な値をリソースの `for_each`/`count` に使うことを許可していません（識別子としてログに出る可能性があるため）。設計段階で気づかず後から修正が必要になるケースが多いです。

4. **third-party モジュール（Terraform Registry）を使う場合は output の sensitive 属性を確認する**：外部モジュールが機密情報を非センシティブな output として公開していないか、事前にソースを確認しましょう。

## 6. クラウド別のシークレット管理との連携

Terraform 単体で完結させず、クラウドネイティブなシークレット管理サービスと組み合わせるのがベストプラクティスです。

- **AWS**：Secrets Manager / SSM Parameter Store（SecureString）と `aws_secretsmanager_secret_version` や `data "aws_secretsmanager_secret_version"` を組み合わせ、Terraform コードには参照のみを残す。RDS では前述の `manage_master_user_password` が有効。
- **GCP**：Secret Manager（`google_secret_manager_secret_version`）を利用し、Cloud SQL の場合は `google_sql_user` のパスワードを `random_password` で生成して Secret Manager に保存するパターンが一般的。
- **Azure**：Key Vault（`azurerm_key_vault_secret`）を利用し、`azurerm_key_vault_secret` の `value` を `sensitive` な output として扱う。Azure AD 経由のマネージド ID と組み合わせることで、Terraform 実行者自身が秘密情報を直接扱わずに済む構成も可能です。

いずれのクラウドでも共通する設計思想は「Terraform に機密情報の生成・注入をさせるのではなく、クラウド側のシークレットストアに保存し、Terraform はその参照（ARN・リソースID）だけを扱う」という点です。これにより state への平文露出リスクを最小化できます。

## 7. 運用上のチェックリスト

- `sensitive = true` を変数・output の両方で徹底しているか
- state のバックエンドは暗号化・アクセス制御されているか
- CI/CD のログに `TF_LOG` を有効にしたまま機密情報が出力されていないか
- `.tfvars` ファイルに直接パスワードを書いていないか（Git 管理対象から除外されているか）
- `terraform show`/`terraform state show` の実行結果を誰でも見られる場所に貼り付けていないか
- Secrets Manager / Key Vault などクラウドネイティブなシークレットストアを優先しているか

## FAQ

**Q1. `sensitive = true` を指定すれば state ファイルも暗号化されますか？**
A. いいえ。`sensitive` はあくまで CLI の plan/apply 出力をマスクする機能で、state ファイル自体の内容には影響しません。state を保護するには、暗号化対応のリモートバックエンド（S3+KMS、GCS+CMEK、Azure Storage+SSE など）を使い、アクセス制御を別途行う必要があります。

**Q2. `terraform output -json` を実行するとセンシティブな値も見えてしまいますが、これは仕様ですか？**
A. はい、仕様です。`sensitive = true` の output でも `-json` オプションを付けると値が平文で表示されます。これは自動化ツールが値を後続処理で使う必要があるための設計です。そのため CI ログに `terraform output -json` の結果をそのまま出力しないよう注意し、必要な値だけを抽出してシークレットストアに直接受け渡す構成にすることが推奨されます。

**Q3. `random_password` で生成した値を Git 管理下の `.tfvars` に書いても大丈夫ですか？**
A. 避けるべきです。`random_password` はリソースとして state に保存されるため十分ですが、生成結果を手動で `.tfvars` にコピーして Git にコミットすると平文の機密情報がリポジトリ履歴に残ってしまいます。生成した値は Secrets Manager や Key Vault などの外部ストアに保存し、参照だけをコードに残す運用にしましょう。

---

Terraform における機密情報の管理は、`sensitive` 属性による出力マスクだけでは不十分であり、state の暗号化・アクセス制御、モジュール設計での伝播漏れ防止、そしてクラウドネイティブなシークレットストアとの連携という三段構えで初めて実用的なセキュリティレベルに到達します。日々の運用の中で「本当にこの値は Terraform の外に出ていないか」を意識し続けることが、事故を未然に防ぐ最大のポイントです。
