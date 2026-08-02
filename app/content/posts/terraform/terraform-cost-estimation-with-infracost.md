---
title: 'Terraform Cost Estimation with Infracost 実践ガイド'
date: 2026-07-30
category: terraform
slug: terraform-cost-estimation-with-infracost
summary: 'Terraform でインフラをコード化していると、`terraform apply` を実行するまで実際の月額コストがわからないという課題に直面します。特にチーム開発では、プルリクエストの時点でコストインパクトを可視化できないと、レビュアーが気づかないまま高額なリソースがマージされてしまうリスクがあります。In…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260730135749.jpg'
lang: ja
---

# Terraform Cost Estimation with Infracost 実践ガイド

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260730135749.jpg)


## はじめに

Terraform でインフラをコード化していると、`terraform apply` を実行するまで実際の月額コストがわからないという課題に直面します。特にチーム開発では、プルリクエストの時点でコストインパクトを可視化できないと、レビュアーが気づかないまま高額なリソースがマージされてしまうリスクがあります。Infracost は、Terraform のプランファイルを解析し、変更前後のコスト差分を静的に見積もるオープンソースツールです。本記事では、Infracost の基本概念から HCL の実例、state との関係、モジュール構成、CI 連携時の注意点までを一通り解説します。

## Infracost とは何か

Infracost は Terraform の `plan` 出力(JSON)を読み込み、各クラウドプロバイダーの公開料金データと照合してコストを算出するコマンドラインツールです。実際に `apply` を実行する必要がなく、プルリクエスト作成時点でコスト差分をコメントとして表示できるのが最大の特徴です。

内部的には以下のステップで動作します。

1. `terraform plan -out=tfplan` でプランバイナリを生成
2. `terraform show -json tfplan` でプランを JSON 化
3. Infracost がその JSON からリソース種別・属性(インスタンスタイプ、ストレージ容量、リージョンなど)を抽出
4. Infracost Cloud Pricing API(または自前のホスト型 API)に問い合わせ、月額換算コストを計算
5. 結果をターミナル出力、Markdown コメント、HTML レポートなどの形式で出力

重要なのは、Infracost は「実測コスト」ではなく「見積もりコスト」を出す点です。トラフィック量やストレージの実使用量に依存する従量課金(データ転送量、リクエスト数など)は、デフォルト値や仮定値を用いた概算になります。

## 基本的な使い方

まずはローカルでの動作確認です。

```bash
# Infracost CLI のインストール(Homebrew の例)
brew install infracost

# API キーの登録(無料枠あり)
infracost auth login

# Terraform ディレクトリに対して直接見積もり
infracost breakdown --path .
```

`--path` にはルートモジュールのディレクトリを指定します。出力例は次のようになります。

```
 Name                                Monthly Qty  Unit         Monthly Cost

 aws_instance.web
 ├─ Instance usage (Linux/UNIX, on-demand, t3.medium)   730  hours       $30.37
 └─ root_block_device
    └─ Storage (general purpose SSD, gp3)                20  GB           $1.60

 OVERALL TOTAL                                                            $31.97
```

## HCL 例:見積もり対象リソースの定義

以下は EC2 インスタンスと RDS を組み合わせたシンプルな構成です。

```hcl
provider "aws" {
  region = "ap-northeast-1"
}

resource "aws_instance" "web" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.medium"

  root_block_device {
    volume_type = "gp3"
    volume_size = 20
  }

  tags = {
    Name = "okpy-web"
  }
}

resource "aws_db_instance" "main" {
  identifier        = "okpy-db"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.small"
  allocated_storage = 50
  storage_type      = "gp3"

  username = "app_user"
  password = var.db_password

  skip_final_snapshot = true
}
```

このコードに対して `infracost breakdown --path .` を実行すると、`aws_instance` と `aws_db_instance` それぞれのコンピュートコストとストレージコストが個別に表示されます。インスタンスタイプを `t3.medium` から `m5.large` に変更した場合の差分を見たい場合は、次のように `diff` サブコマンドを使います。

```bash
infracost diff --path . --compare-to infracost-base.json
```

事前に `infracost breakdown --path . --format json --out-file infracost-base.json` でベースラインを保存しておくことで、変更前後のコスト差分を数値で確認できます。

## Terraform state との関係

Infracost はデフォルトでは `terraform plan` の JSON 出力のみを参照し、リモートの state ファイルには直接アクセスしません。ただし、既存リソースの現在の設定値(インスタンスタイプやストレージサイズなど)は plan の中に "no-op" または "update" の変更として含まれるため、間接的に state の内容が反映されます。

state を持たない `terraform plan` (初回適用前)でも見積もりは可能ですが、既存インフラとの差分表示(`infracost diff`)を行う場合は、実行環境が正しい state をバックエンドから読み込めることが前提になります。S3 や GCS などのリモートバックエンドを使っている場合、CI 実行環境に適切な認証情報(IAM ロールやサービスアカウント)を渡しておく必要があります。

```hcl
terraform {
  backend "s3" {
    bucket = "okpy-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "ap-northeast-1"
  }
}
```

state ロックがかかっている最中に CI がプラン生成を行うと競合が発生することがあるため、Infracost 用のプラン生成は読み取り専用(`terraform plan` のみで `apply` を伴わない)であっても、state ロックの挙動を意識しておくと安全です。

## モジュール構成での見積もり

実際のプロジェクトでは、リソースを直接書くのではなく Terraform モジュールを介して構成することが一般的です。Infracost はモジュール内部のリソースも問題なく解析します。

```hcl
module "web_server" {
  source        = "./modules/ec2"
  instance_type = "t3.medium"
  volume_size   = 20
}

module "database" {
  source            = "./modules/rds"
  instance_class    = "db.t3.small"
  allocated_storage = 50
}
```

複数モジュール・複数環境(dev/staging/prod)を持つ場合は、`infracost-usage.yml` や設定ファイル `infracost.yml` を使って一括管理すると効率的です。

```yaml
version: 0.1
projects:
  - path: environments/dev
    name: okpy-dev
  - path: environments/staging
    name: okpy-staging
  - path: environments/prod
    name: okpy-prod
```

この設定ファイルを使えば、`infracost breakdown --config-file infracost.yml` 一発ですべての環境のコストをまとめて出力できます。モジュールが多段になっている大規模プロジェクトほど、この一括設定の恩恵は大きくなります。

## 従量課金リソースの扱い(usage ファイル)

S3 のリクエスト数や Lambda の実行回数、データ転送量など、Terraform の定義だけからは算出できない項目については、Infracost の usage ファイルで仮定値を明示的に指定します。

```yaml
version: 0.1
resource_usage:
  aws_lambda_function.api:
    monthly_requests: 1000000
    average_request_duration: 300
  aws_s3_bucket.assets:
    storage_gb: 500
    monthly_tier_1_requests: 200000
```

```bash
infracost breakdown --path . --usage-file infracost-usage.yml
```

usage ファイルを設定しないと、従量課金部分は「0」または非表示として扱われるため、実態と乖離した過小評価になりがちです。特に Lambda、S3、CloudFront、データ転送量が絡む構成では usage ファイルの整備を強く推奨します。

## CI/CD との連携

Infracost の真価は CI パイプラインに組み込んでこそ発揮されます。GitHub Actions での典型例は以下の通りです。

```yaml
name: infracost
on: [pull_request]

jobs:
  infracost:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: infracost/actions/setup@v3
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}
      - run: infracost breakdown --path . --format json --out-file /tmp/infracost.json
      - uses: infracost/actions/comment@v3
        with:
          path: /tmp/infracost.json
          behavior: update
```

これにより、プルリクエストごとにコスト差分が自動でコメントされ、レビュアーが変更のコストインパクトを一目で把握できるようになります。

## クラウドプロバイダーとの関係

Infracost は AWS を中心にリソースカバレッジが最も広く、EC2、RDS、S3、Lambda、EKS など主要サービスをほぼ網羅しています。Google Cloud(GCP)についても Compute Engine、Cloud SQL、GKE、Cloud Storage など主要リソースに対応していますが、一部のマネージドサービス(新しめの GCP サービスなど)はカバレッジが AWS より遅れる傾向があります。Azure についても Virtual Machines、Azure SQL Database、AKS などの主要リソースに対応しています。

いずれのプロバイダーも、料金は公開されているオンデマンド料金・リザーブド料金・Savings Plan を基準にしており、企業ごとの個別割引契約(Enterprise Discount Program や Committed Use Discount など)は反映されません。正確な社内コストと比較したい場合は、Infracost Cloud のプライシング API に自社の割引率を設定する機能を利用するか、見積もり結果をあくまで「相対的な差分の目安」として扱うのが現実的です。

## 注意点

- **見積もりはあくまで概算**:従量課金部分は usage ファイルの仮定値に依存するため、実際の請求額と一致するとは限りません。
- **カバレッジの限界**:マイナーなリソースタイプやカスタムプロバイダーのリソースは価格データが存在せず、`No price information found` として無視されることがあります。
- **マルチクラウド構成の集計**:AWS と GCP を併用する構成では、通貨単位や課金体系(秒単位課金 vs 分単位課金など)の違いを意識して結果を読む必要があります。
- **API キーの管理**:CI で使う `INFRACOST_API_KEY` はリポジトリのシークレットとして管理し、平文でコミットしないようにします。
- **プラン生成時の副作用**:`terraform plan` 自体がプロバイダー API を呼び出すため、大規模な state に対して頻繁に CI 実行すると API レートリミットに達することがあります。

## FAQ

**Q1. Infracost は無料で使えますか?**
CLI 自体はオープンソースで無料です。個人・小規模チーム向けの無料枠が用意されており、Infracost Cloud のダッシュボードやポリシー機能など高度な機能は有料プランが必要になる場合があります。基本的なコスト見積もりとプルリクエストコメント機能は無料枠でも十分に利用できます。

**Q2. Terraform Cloud や Terraform Enterprise と併用できますか?**
可能です。Terraform Cloud の Run Task 機能や API 経由でプラン出力を取得し、Infracost に渡すことで同様のコスト差分表示が実現できます。CI 上で `terraform plan` を実行するワークフローと基本的な統合方法は変わりません。

**Q3. 見積もり結果と実際の請求額が大きくずれる場合はどうすればよいですか?**
まず usage ファイルに設定した従量課金の仮定値が実態と合っているか確認します。次に、企業向け割引(RI、Savings Plan、EDP など)が反映されていないことが原因であることが多いため、Infracost Cloud のプライシング設定で自社の割引率を反映するか、見積もりを「絶対値」ではなく「変更前後の相対差分」として活用する運用に切り替えることを推奨します。

## まとめ

Infracost は Terraform のワークフローに「コストの可視化」という重要な観点を追加してくれるツールです。HCL の記述からモジュール構成、CI パイプラインへの統合まで一貫して組み込むことで、インフラ変更のレビュープロセスにコスト意識を自然に組み込むことができます。まずはローカルでの `infracost breakdown` から試し、usage ファイルを整備しながら CI に組み込んでいくのが導入の王道です。
