---
title: 'Terraform Cloud によるリモート操作実践ガイド'
date: 2026-08-08
category: terraform
slug: terraform-remote-operations-with-terraform-cloud
summary: 'Terraform をチームで運用していると、ローカル環境での `terraform apply` にはさまざまな課題が出てきます。実行環境の差異、認証情報の管理、state ファイルの競合、承認フローの欠如などです。Terraform Cloud（TFC）が提供する「リモート操作（Remote Operatio…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260808081831.jpg'
lang: ja
---

# Terraform Cloud によるリモート操作実践ガイド

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260808081831.jpg)


## はじめに

Terraform をチームで運用していると、ローカル環境での `terraform apply` にはさまざまな課題が出てきます。実行環境の差異、認証情報の管理、state ファイルの競合、承認フローの欠如などです。Terraform Cloud（TFC）が提供する「リモート操作（Remote Operations）」は、これらの課題を解決するための仕組みで、`plan` や `apply` を Terraform Cloud 上のリモートワーカーで実行し、state の保存・ロック・共有までを一元管理できます。

本記事では、Terraform Cloud のリモート操作の概念から、実際の HCL 設定例、state 管理、モジュール活用、運用上の注意点までを実践的に解説します。

## リモート操作とは何か

通常の Terraform はローカルマシン上でプロバイダーの API を呼び出し、state ファイルをローカルまたは手動設定したバックエンド（S3 など）に保存します。一方、Terraform Cloud のリモート操作では、次のような流れになります。

1. ローカルで `terraform plan` や `apply` を実行すると、設定とコード差分が Terraform Cloud に送信される
2. Terraform Cloud 上の隔離されたリモートワーカー（コンテナ）で実際の実行が行われる
3. 実行ログはストリーミングでローカルのターミナルにも表示される
4. state は Terraform Cloud のバックエンドに自動的に保存・バージョン管理される

これにより、実行環境が統一され、認証情報をローカルマシンに置く必要がなくなり、複数人での同時実行による state 破損のリスクも大幅に減ります。また、VCS（GitHub、GitLab、Bitbucket など）と連携すれば、プルリクエスト単位で自動的に plan が走る CI/CD 的なワークフローも実現できます。

Terraform Cloud には主に3つの実行モードがあります。

- **Remote**: 上記のようにリモートワーカーで実行（デフォルトかつ推奨）
- **Local**: state の保存先としてのみ TFC を使い、実行自体はローカルで行う
- **Agent**: TFC Agent を使い、TFC のネットワークから届かないプライベート環境（オンプレミスや閉域網の VPC 内など）でリモート実行を行う

## HCL での設定例

### Cloud ブロックによる接続

Terraform 1.1 以降では `cloud` ブロックを使って Organization と Workspace を指定します。

```hcl
terraform {
  cloud {
    organization = "okpy-org"

    workspaces {
      name = "prod-network"
    }
  }
}
```

`terraform login` コマンドで API トークンを取得・保存すれば、`terraform init` を実行するだけでリモートバックエンドとして接続されます。

```bash
terraform login
terraform init
```

### タグベースで複数 Workspace を扱う場合

モノレポで複数の Workspace を切り替えたい場合は `name` の代わりに `tags` を使うこともできます（Terraform 1.6 以降）。

```hcl
terraform {
  cloud {
    organization = "okpy-org"

    workspaces {
      tags = ["network", "production"]
    }
  }
}
```

### 変数の設定

リモート実行では、環境変数や Terraform 変数を Workspace 側にも設定できます。機密情報（AWS のアクセスキーなど）は Sensitive フラグを付けて TFC の Web UI や API から登録するのが安全です。

```hcl
variable "instance_type" {
  type    = string
  default = "t3.micro"
}

resource "aws_instance" "web" {
  ami           = "ami-0abcdef1234567890"
  instance_type = var.instance_type

  tags = {
    Name = "okpy-web"
  }
}
```

Workspace の Variables 画面で `AWS_ACCESS_KEY_ID` や `AWS_SECRET_ACCESS_KEY` を Environment Variable として Sensitive 設定すれば、リモートワーカー内でのみ利用され、ログにも出力されません。

## state の管理

Terraform Cloud を使う最大のメリットの一つが state 管理の自動化です。

- **保存場所の一元化**: state はローカルディスクではなく TFC 内に保存され、チーム全員が同じ state を参照します
- **自動ロック**: `apply` 実行中は自動的に state がロックされ、同時実行による競合を防ぎます
- **バージョン履歴**: state の変更履歴が自動的に記録され、過去のバージョンと差分を確認できます
- **暗号化**: 保存時・転送時ともに暗号化されます

既存のローカル state や S3 バックエンドから移行する場合は、`terraform init` 実行時に state のインポートを促されます。

```bash
terraform init -migrate-state
```

state の中身を直接確認したい場合は次のコマンドが便利です。

```bash
terraform state list
terraform state show aws_instance.web
```

なお、TFC 上の state を CLI から直接書き換える操作（`terraform state rm` など）もリモート実行の一環として扱われるため、ロックの仕組みが働きます。

## モジュールの活用

Terraform Cloud には Private Registry 機能があり、社内向けに共有したいモジュールを VCS リポジトリと連携させてバージョン管理付きで公開できます。

```hcl
module "vpc" {
  source  = "app.terraform.io/okpy-org/vpc/aws"
  version = "2.3.0"

  cidr_block = "10.0.0.0/16"
  name       = "okpy-prod-vpc"
}
```

Public Registry のモジュールと同様に `source` に Organization 名を含めた形式で参照します。バージョンを固定することで、意図しない破壊的変更の混入を防げます。

複数の Workspace で共通のネットワーク構成やタグ付けルールを使う場合は、モジュールを介して DRY に保つのが定石です。ただし、モジュールを細かく分割しすぎると `plan` の可読性が落ちるため、責務単位（VPC、IAM、アプリケーション基盤など）でまとめるのが実務上扱いやすいでしょう。

## クラウドプロバイダーとの関係

Terraform Cloud 自体は特定のクラウドに依存しない実行基盤であり、AWS・GCP・Azure いずれのプロバイダーとも組み合わせて使えます。

- **AWS**: `aws` プロバイダーの認証情報を Workspace の環境変数（`AWS_ACCESS_KEY_ID` など）や、OIDC を使った Dynamic Provider Credentials で渡すのが一般的です。IAM ロールの Assume Role と組み合わせることで、長期的なアクセスキーを持たない構成も可能です
- **GCP**: サービスアカウントの JSON キーを `GOOGLE_CREDENTIALS` として登録するか、こちらも Workload Identity 連携による OIDC 認証が推奨されます
- **Azure**: サービスプリンシパルの `ARM_CLIENT_ID` / `ARM_CLIENT_SECRET` / `ARM_TENANT_ID` / `ARM_SUBSCRIPTION_ID` を環境変数として設定します

いずれの場合も、TFC の Dynamic Provider Credentials（OIDC ベース）を使うことで、静的な認証情報を Workspace に保存せずに済み、セキュリティ面で大きなメリットがあります。マルチクラウド構成のプロジェクトでも、Workspace を分けることでクラウドごとに state と権限を分離管理できます。

## 運用上の注意点

- **コスト管理**: Terraform Cloud の Free tier には Workspace 数やリソース管理数に制限があります。組織の規模に応じて Team & Governance プランや Business プランへの移行を検討してください
- **Sentinel / OPA によるポリシー適用**: 有償プランでは Sentinel（または OPA）を使い、「本番環境では特定インスタンスタイプ以外禁止」といったポリシーを `plan` 段階で強制できます。ガバナンスが必要な組織では早めに導入設計しておくと後々の手戻りが減ります
- **Apply の承認フロー**: デフォルトでは `apply` 前に人手による承認（Manual Apply）が挟まりますが、CI/CD に組み込む場合は Auto Apply への切り替えも検討します。ただし本番 Workspace では手動承認を残すのが無難です
- **Workspace 間の依存関係**: `terraform_remote_state` データソースや Run Triggers を使って Workspace 間の依存を表現できますが、依存が複雑になりすぎるとトラブルシュートが難しくなるため、依存グラフはシンプルに保つことを意識してください
- **ネットワーク制約**: リモートワーカーはインターネット経由でクラウド API にアクセスします。閉域網内のリソースを操作する場合は TFC Agent の導入が必須です
- **ログとシークレットの取り扱い**: Sensitive 変数として登録しない限りログに出力される可能性があるため、シークレットは必ず Sensitive フラグを付け、可能であれば Vault などの外部シークレット管理と連携することを推奨します

## FAQ

**Q1. Terraform Cloud の Free プランでもリモート操作は使えますか？**

はい、使えます。Free プランでも `cloud` ブロックによるリモート実行、state 管理、VCS 連携といった基本機能は利用可能です。ただし Sentinel によるポリシー制御や SSO、詳細な監査ログなどのガバナンス機能は上位プランが必要です。小規模チームやまず試してみたい場合は Free プランから始めるのがおすすめです。

**Q2. ローカルの `terraform apply` と何が違うのですか？速度が遅くなりませんか？**

実行自体はリモートワーカー上で行われるため、ローカルマシンのスペックやネットワーク環境に依存しなくなり、むしろ安定します。多少のオーバーヘッド（ジョブのキューイングやログストリーミング）はありますが、複数人での state 競合や「自分の環境でしか動かない」問題が解消されるメリットの方が大きいです。速度面が特に気になる場合は Agent 実行モードでネットワーク遅延を最小化することも検討できます。

**Q3. 既存の S3 + DynamoDB バックエンドから Terraform Cloud に移行するのは大変ですか？**

`backend` ブロックを `cloud` ブロックに書き換え、`terraform init -migrate-state` を実行するだけで基本的な移行は完了します。既存の state ファイルはそのまま TFC にインポートされるため、リソースの再作成は発生しません。ただし、移行前には必ず state のバックアップを取得し、複数人が同時に `apply` を実行しないよう調整することを強く推奨します。移行後は IAM やサービスアカウントの認証情報を Workspace 側に再設定する作業も忘れずに行いましょう。

## まとめ

Terraform Cloud のリモート操作は、単なる「実行環境をクラウドに移す」機能にとどまらず、state のロック・共有、VCS 連携による自動 plan、Sentinel によるポリシー適用など、チームでの IaC 運用を安全かつスケーラブルにするための土台です。AWS・GCP・Azure のいずれを使う場合でも、Dynamic Provider Credentials を使った OIDC 認証を組み合わせることで、静的なシークレットを持たないセキュアな構成が実現できます。まずは Free プランで小さな Workspace を作り、`cloud` ブロックでの接続とリモート `plan`/`apply` の挙動を体験してみることをおすすめします。
