---
title: 'Terraform と GitHub を連携させる実践ガイド'
date: 2026-10-12
category: terraform
slug: terraform-github
summary: 'Terraform はクラウドリソースだけでなく、GitHub のリポジトリ、ブランチ保護、Webhook、チーム権限などもコードとして管理できます。公式の `integrations/github` プロバイダーを使うことで、GitHub 上の設定を Infrastructure as Code（IaC）として…'
lang: ja
---

# Terraform と GitHub を連携させる実践ガイド

## はじめに

Terraform はクラウドリソースだけでなく、GitHub のリポジトリ、ブランチ保護、Webhook、チーム権限などもコードとして管理できます。公式の `integrations/github` プロバイダーを使うことで、GitHub 上の設定を Infrastructure as Code（IaC）として一元管理し、レビュー可能な形で変更履歴を残すことができます。本稿では GitHub プロバイダーの基本概念から HCL の実例、state 管理、モジュール化、運用上の注意点までを体系的に解説します。

## 1. GitHub プロバイダーの概念

Terraform の GitHub プロバイダーは、GitHub の REST API / GraphQL API をラップし、以下のようなリソースを宣言的に管理できます。

- リポジトリ本体（`github_repository`）
- ブランチ保護ルール（`github_branch_protection`）
- チームとメンバーシップ（`github_team`, `github_team_membership`）
- コラボレーターの権限（`github_repository_collaborator`）
- Webhook（`github_repository_webhook`）
- Secrets（`github_actions_secret`）
- ラベル、Issue テンプレートなど

クラウドプロバイダー（AWS/GCP/Azure）がインフラのリソースを扱うのに対し、GitHub プロバイダーは「開発プロセスそのもの」をコード化する点が特徴です。たとえば「新規リポジトリ作成時に必ずブランチ保護を設定する」「特定チームに自動的に権限を付与する」といったポリシーを、手動のクリック操作ではなくコードレビューを経て変更できるようになります。

### 認証

GitHub プロバイダーは Personal Access Token（PAT）、GitHub App、または OAuth トークンで認証します。GitHub Actions 上で実行する場合は GitHub App のインストールトークンを使うのが推奨されます。PAT は漏洩時のリスクが大きく、スコープも広くなりがちなため、組織運用では GitHub App 認証への移行を検討してください。

```hcl
terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "github" {
  owner = "your-org"
  # token は環境変数 GITHUB_TOKEN から自動的に読み込まれる
}
```

トークンをコードにハードコーディングせず、環境変数や Terraform Cloud の Workspace 変数、GitHub Actions の Secrets から注入するのが基本です。

## 2. HCL の実例

### リポジトリの作成

```hcl
resource "github_repository" "app" {
  name        = "okpy-app"
  description = "OKPy サービス本体"
  visibility  = "private"

  has_issues   = true
  has_projects = false
  has_wiki     = false

  delete_branch_on_merge = true

  template {
    owner      = "your-org"
    repository = "service-template"
  }
}
```

### ブランチ保護

```hcl
resource "github_branch_protection" "main" {
  repository_id = github_repository.app.node_id
  pattern       = "main"

  required_status_checks {
    strict   = true
    contexts = ["ci/test", "ci/lint"]
  }

  required_pull_request_reviews {
    required_approving_review_count = 1
    dismiss_stale_reviews           = true
  }

  enforce_admins = true
}
```

### チームと権限

```hcl
resource "github_team" "backend" {
  name        = "backend-team"
  description = "バックエンド開発チーム"
  privacy     = "closed"
}

resource "github_team_repository" "backend_access" {
  team_id    = github_team.backend.id
  repository = github_repository.app.name
  permission = "push"
}
```

### Actions Secrets

```hcl
resource "github_actions_secret" "aws_role" {
  repository      = github_repository.app.name
  secret_name     = "AWS_ROLE_ARN"
  plaintext_value = var.aws_role_arn
}
```

機密値は `plaintext_value` に直接埋め込まず、`var.*` や外部の Secret 管理（AWS Secrets Manager、GCP Secret Manager など）から取得する構成にすることで、state ファイルへの平文漏洩リスクを抑えられます（ただし後述のとおり state 自体の暗号化は別途必要です）。

## 3. state の扱い

GitHub リソースの state 管理はクラウドリソースと同様に重要ですが、いくつか GitHub 特有の注意点があります。

- **Secrets は暗号化されて API に送られるが、state 上は構成次第で機微情報が残る**ため、state ファイルを S3 や Terraform Cloud の暗号化バックエンドに保存し、ローカルや Git リポジトリには絶対にコミットしないこと。
- **GitHub App のインストール ID やチーム ID など、コンソール操作で後から変わる値を持つリソース**は `terraform import` で既存リソースを取り込んでから運用に乗せると、意図しない削除・再作成を防げます。

```bash
terraform import github_repository.app okpy-app
```

- リモートバックエンドの例（AWS S3 + DynamoDB ロック）:

```hcl
terraform {
  backend "s3" {
    bucket         = "your-org-tfstate"
    key            = "github/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "tfstate-lock"
    encrypt        = true
  }
}
```

GCS や Azure Blob Storage をバックエンドにする場合も同様に、暗号化とロック機構（GCS はネイティブにロックをサポート、Azure Blob は Lease で代替）を有効にしてください。

- **ドリフト検知**: GitHub の設定は Web UI からも変更可能なため、Terraform 管理外の変更（ドリフト）が発生しやすいです。`terraform plan` を CI で定期実行し、差分が出たら通知する運用を組み込むことを推奨します。

## 4. モジュール化

複数のリポジトリに共通のポリシー（ブランチ保護、Webhook、ラベルなど）を適用する場合は、モジュール化してコードの重複を避けます。

```hcl
# modules/standard-repo/main.tf
variable "repo_name" {
  type = string
}

variable "team_id" {
  type = string
}

resource "github_repository" "this" {
  name                    = var.repo_name
  visibility              = "private"
  delete_branch_on_merge  = true
}

resource "github_branch_protection" "this" {
  repository_id = github_repository.this.node_id
  pattern       = "main"

  required_pull_request_reviews {
    required_approving_review_count = 1
  }
}

resource "github_team_repository" "this" {
  team_id    = var.team_id
  repository = github_repository.this.name
  permission = "push"
}

output "repository_url" {
  value = github_repository.this.html_url
}
```

呼び出し側:

```hcl
module "app_repo" {
  source    = "./modules/standard-repo"
  repo_name = "okpy-app"
  team_id   = github_team.backend.id
}

module "batch_repo" {
  source    = "./modules/standard-repo"
  repo_name = "okpy-batch"
  team_id   = github_team.backend.id
}
```

組織全体で使う場合は、モジュールを別リポジトリに切り出して Terraform Registry（プライベート含む）に公開し、バージョンタグ（`source = "git::https://github.com/your-org/tf-modules.git//github-repo?ref=v1.2.0"`）で参照すると変更の影響範囲を制御しやすくなります。

## 5. 注意点

1. **API レートリミット**: GitHub API には時間あたりのリクエスト制限があります。多数のリポジトリを一括管理する場合、`terraform apply` が失敗することがあるため、GitHub App 認証（レートリミットが PAT より高い）への切り替えや `-parallelism` オプションでの並列度調整を検討してください。

2. **破壊的変更に注意**: `github_repository` の `name` を変更すると、Terraform はリソースを削除・再作成しようとする場合があります。意図しないリポジトリの削除を防ぐため、`prevent_destroy` を活用するか、`terraform plan` の内容を必ず確認してから `apply` してください。

3. **Organization 設定との競合**: GitHub Organization 側でデフォルトのブランチ保護やチーム権限ポリシーが設定されている場合、Terraform の設定と競合してドリフトが発生し続けることがあります。Organization の管理方針と Terraform の管理範囲を事前にすり合わせておくことが重要です。

4. **Secrets のローテーション**: `github_actions_secret` で管理する値を変更した場合、plan 上は常に差分が「known after apply」と表示されます（GitHub API が暗号化済みの値を返さないため）。これは仕様であり不整合ではありません。

5. **権限スコープの最小化**: Terraform を実行する GitHub App / PAT には、管理対象のリポジトリ・Organization に対する必要最小限の権限のみを付与してください。CI/CD パイプライン上で実行する場合は、実行ジョブのスコープも制限します。

## 6. AWS / GCP / Azure との関係

GitHub プロバイダー単体でも価値はありますが、多くの現場ではクラウドリソースと組み合わせて使われます。

- **AWS**: GitHub Actions から AWS へデプロイする際の OIDC Identity Provider（`aws_iam_openid_connect_provider`）や IAM Role を Terraform で作成し、対応する `AWS_ROLE_ARN` を `github_actions_secret` や Variables として同じ Terraform コード内で設定することで、クラウド側と GitHub 側の設定を一つの `apply` で同期できます。
- **GCP**: Workload Identity Federation を使い、GitHub Actions から GCP サービスアカウントへ認証する構成も同様に、`google_iam_workload_identity_pool` と GitHub 側の Secrets/Variables をまとめて管理すると整合性が取りやすくなります。
- **Azure**: Azure AD のフェデレーション資格情報（Federated Identity Credential）を Terraform の `azurerm` プロバイダーで作成し、GitHub Actions のワークフローから Azure へのパスワードレス認証を実現するパターンがよく使われます。

いずれの場合も、クラウド側のプロバイダー（`aws`, `google`, `azurerm`）と `github` プロバイダーを同一の Terraform ルートモジュール、あるいは依存関係のある別ステートとして構成し、`terraform_remote_state` やモジュール出力で ARN・ID を橋渡しするのが典型的な設計です。

## FAQ

**Q1. GitHub プロバイダーの認証に PAT ではなく GitHub App を使うべき理由は？**

PAT は個人アカウントに紐づくため、退職や権限変更の影響を受けやすく、またレートリミットも低めです。GitHub App はインストール単位でスコープを絞れ、組織としてのライフサイクル管理がしやすく、API のレートリミットも高いため、CI/CD や本格的な IaC 運用では GitHub App 認証への移行が推奨されます。

**Q2. Terraform で管理しているリポジトリを手動で GitHub UI から変更したらどうなりますか？**

次回の `terraform plan` で UI 側の変更がドリフトとして検出され、Terraform の定義に戻すような差分が表示されます。意図した変更であれば、先に HCL を更新してから `apply` する運用を徹底し、UI からの直接変更は原則禁止するルールを設けるのが安全です。

**Q3. 既存の大量のリポジトリを一括で Terraform 管理に移行する良い方法はありますか？**

`terraform import` をリポジトリごとに実行するのは手間がかかるため、`terraformer` などのサードパーティ製インポートツールや、GitHub API を使って既存リソース一覧を取得し `import` ブロック（Terraform 1.5 以降の宣言的 import）を自動生成するスクリプトを書くアプローチが現実的です。移行は小さいリポジトリ群から段階的に進め、state の整合性を都度確認することをお勧めします。

## まとめ

GitHub プロバイダーを使った Terraform 運用は、リポジトリ設定・ブランチ保護・チーム権限・Secrets といった開発プロセスの土台をコードとレビューで管理可能にする強力な手段です。state の暗号化と保管場所、API レートリミット、破壊的変更への警戒、Organization 設定との整合性といった注意点を踏まえつつ、モジュール化によって複数リポジトリへのポリシー適用を効率化することで、スケーラブルで安全な GitHub 運用基盤を構築できます。クラウドプロバイダーと組み合わせることで、OIDC/Workload Identity を用いたパスワードレスなデプロイ連携まで一貫してコード化できる点も、GitHub プロバイダーを採用する大きなメリットです。
