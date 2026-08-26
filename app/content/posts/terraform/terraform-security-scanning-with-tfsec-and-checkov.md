---
title: 'Terraform セキュリティスキャン実践ガイド：tfsec と Checkov で IaC を守る'
date: 2026-08-26
category: terraform
slug: terraform-security-scanning-with-tfsec-and-checkov
summary: 'Terraform でインフラをコード化(IaC)することは、再現性とレビュー可能性という大きな利点をもたらします。しかし、コードとして書かれているからこそ、誤った設定がそのまま本番環境に反映されてしまうリスクも同時に抱えています。パブリックに公開された S3 バケット、暗号化されていないディスク、過剰な IAM…'
lang: ja
---

# Terraform セキュリティスキャン実践ガイド：tfsec と Checkov で IaC を守る

## はじめに

Terraform でインフラをコード化(IaC)することは、再現性とレビュー可能性という大きな利点をもたらします。しかし、コードとして書かれているからこそ、誤った設定がそのまま本番環境に反映されてしまうリスクも同時に抱えています。パブリックに公開された S3 バケット、暗号化されていないディスク、過剰な IAM 権限などは、コードレビューの目視だけでは見落とされがちです。

こうした問題を自動的に検出するために使われるのが、静的解析(SAST for IaC)ツールである **tfsec** と **Checkov** です。本記事では、両ツールの概念、実際の HCL コード例、State ファイルの扱い、モジュール構成での注意点、そして CI への組み込み方までを実践的に解説します。

## 1. 概念：なぜ IaC にセキュリティスキャンが必要か

Terraform のコードは「宣言」であり、`terraform apply` を実行するまでは実際のリソースに影響しません。この特性を活かし、**apply の前にコードそのものを検査する**ことで、問題を早期に、しかも低コストで修正できます。これが「シフトレフト」と呼ばれる考え方です。

tfsec と Checkov はどちらも、HCL ファイル(または plan の JSON 出力)を静的に解析し、あらかじめ定義されたセキュリティルール(ポリシー)に違反していないかをチェックします。動作イメージは以下の通りです。

- **tfsec**: Aqua Security が開発した Go 製ツール。Terraform に特化しており、軽量・高速。近年は Trivy のサブコマンド(`trivy config`)に統合される方向に進んでいます。
- **Checkov**: Bridgecrew(現 Prisma Cloud)が開発した Python 製ツール。Terraform だけでなく CloudFormation、Kubernetes、Dockerfile など多様な IaC 形式に対応する汎用スキャナーです。

両者ともルールベースでリソース属性を検査し、「暗号化が有効か」「パブリックアクセスが許可されていないか」「ログが有効か」といった観点で警告を出します。

## 2. インストールと基本的な使い方

```bash
# tfsec のインストール(Homebrew の場合)
brew install tfsec

# Checkov のインストール(pip の場合)
pip install checkov
```

基本的なスキャンはディレクトリを指定するだけです。

```bash
# tfsec の実行
tfsec ./infra

# Checkov の実行
checkov -d ./infra
```

どちらも終了コードで CI のパス/フェイルを判定できるため、パイプラインへの組み込みが容易です。

## 3. HCL 例で見る典型的な指摘事項

### 3.1 パブリックアクセスを許可した S3 バケット(AWS)

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "okpy-example-logs"
}

resource "aws_s3_bucket_acl" "logs_acl" {
  bucket = aws_s3_bucket.logs.id
  acl    = "public-read"
}
```

上記のコードに対して、tfsec は `aws-s3-no-public-access-with-acl`、Checkov は `CKV_AWS_20` などのルールで警告を出します。修正例は以下の通りです。

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "okpy-example-logs"
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}
```

### 3.2 暗号化されていないディスク(GCP)

```hcl
resource "google_compute_disk" "default" {
  name = "okpy-disk"
  zone = "asia-northeast1-a"
  size = 50
}
```

Checkov は `CKV_GCP_37`(顧客管理鍵の未使用)などを指摘します。GCP はデフォルトで保存時暗号化が有効ですが、コンプライアンス要件によっては CMEK(Customer-Managed Encryption Key)の指定が求められることがあります。

```hcl
resource "google_compute_disk" "default" {
  name = "okpy-disk"
  zone = "asia-northeast1-a"
  size = 50

  disk_encryption_key {
    kms_key_self_link = google_kms_crypto_key.disk_key.id
  }
}
```

### 3.3 過度に緩いネットワークセキュリティグループ(Azure)

```hcl
resource "azurerm_network_security_rule" "allow_ssh" {
  name                       = "allow-ssh"
  priority                   = 100
  direction                  = "Inbound"
  access                     = "Allow"
  protocol                   = "Tcp"
  source_port_range          = "*"
  destination_port_range     = "22"
  source_address_prefix      = "*"
  destination_address_prefix = "*"
  resource_group_name        = azurerm_resource_group.example.name
  network_security_group_name = azurerm_network_security_group.example.name
}
```

`source_address_prefix = "*"` は全世界からの SSH アクセスを許可してしまうため、tfsec の `azure-network-no-public-ingress` などで検出されます。踏み台サーバーの IP や社内 VPN の CIDR に限定するのが基本です。

## 4. State ファイルとの関係

tfsec と Checkov は基本的に **HCL ソースコードを静的に解析**するツールであり、`terraform.tfstate` そのものをスキャン対象にするわけではありません。しかし、実運用では以下の点に注意が必要です。

- **State ファイルの機密情報**: state には、パスワードやアクセスキーなど機微な値が平文で格納されることがあります。tfsec/Checkov はコードの設定ミスを検出するツールであり、state 自体の暗号化や保管場所の安全性(S3 + KMS、Terraform Cloud のリモート State など)は別途担保する必要があります。
- **Plan ベースのスキャン**: Checkov は `terraform plan -out=tfplan.binary` から生成した JSON(`terraform show -json tfplan.binary > tfplan.json`)を解析する機能もあり、変数展開後の「実際に適用される値」を検査できます。動的な値(データソースや変数)がリソース属性に影響する場合は、コードだけを見るより plan ベースの方が正確に評価できます。
- **ドリフト検出との違い**: tfsec/Checkov は「これから適用するコード」の妥当性を見るものであり、既に構築済みのクラウド環境が実際にコードと一致しているか(ドリフト)は検出しません。ドリフト検出には `terraform plan` の差分確認や、Driftctl のような別ツールを併用します。

## 5. モジュール構成での注意点

再利用可能なモジュールを設計する場合、スキャンの実施タイミングと粒度に工夫が必要です。

- **モジュール単体でスキャンする**: 呼び出し元(ルートモジュール)だけでなく、`modules/` 配下の各モジュールも個別にスキャン対象に含めます。ルートだけをスキャンすると、モジュール内部のデフォルト値の危険性を見逃すことがあります。
- **外部モジュールのスキャン**: Terraform Registry などから取得したサードパーティモジュールも `.terraform/modules` 配下に展開されるため、`terraform init` 後にスキャンすることで、依存先モジュールの設定も検査対象に含められます。ただし、外部モジュールの指摘は自分たちで修正できないケースも多く、バージョン固定と代替モジュールの検討が現実的な対応になります。
- **除外ルールの明示**: あえて緩い設定を許容する場合(検証環境など)は、コード中にインラインコメントでルールを除外するのが望ましいプラクティスです。

```hcl
resource "aws_s3_bucket_acl" "dev_public" {
  # tfsec:ignore:aws-s3-no-public-access-with-acl -- 検証環境の一時的な公開設定のため
  bucket = aws_s3_bucket.dev.id
  acl    = "public-read"
}
```

Checkov も同様に `#checkov:skip=CKV_AWS_20:検証環境のため許容` のようなコメントでスキップ理由を明記できます。理由を書かないサイレントな除外は、後から見たときに意図が分からなくなるため避けるべきです。

## 6. CI パイプラインへの組み込み

GitHub Actions での最小構成例です。

```yaml
name: iac-security-scan
on: [pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tfsec
        uses: aquasecurity/tfsec-action@v1.0.3
        with:
          working_directory: infra
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: infra
          quiet: true
```

PR 作成時に自動でスキャンが走り、重大な指摘があればマージをブロックする運用にすることで、レビュアーの負担を減らしつつ品質を底上げできます。

## 7. AWS・GCP・Azure との関係

tfsec と Checkov はいずれもマルチクラウド対応であり、AWS・GCP・Azure それぞれに専用のルールセットを持っています。共通する検査観点は「暗号化の有効化」「パブリックアクセスの制限」「ログ・監査証跡の有効化」「最小権限の原則」です。一方で、クラウドごとに固有のサービス(AWS の IAM ポリシー、GCP の Organization Policy、Azure の RBAC)に対応したルールも用意されているため、マルチクラウド構成のリポジトリでは両ツールを併用し、カバレッジの差分を補完し合うのが実践的です。

## 8. 注意点まとめ

- スキャンは「保険」であり、設計段階でのセキュアな構成方針(最小権限、暗号化必須など)を代替するものではありません。
- ルールの重大度(Critical/High/Medium/Low)を精査せずに全件をブロックすると、開発速度を著しく損ないます。段階的に重大度の高いものからブロック対象にするのが現実的です。
- ツールのバージョンによってルールが追加・変更されるため、CI 上でのツールバージョンを固定し、意図しない挙動変化を防ぎます。
- 誤検知(False Positive)は必ず発生します。除外は個別リソース単位で理由付きに留め、ルール自体を丸ごと無効化することは避けましょう。

## FAQ

**Q1. tfsec と Checkov、どちらか一方だけ導入すればよいですか？**
A. 目的が Terraform に限定されるなら tfsec だけでも十分な場合が多いですが、Checkov は Kubernetes マニフェストや Dockerfile なども検査できるため、IaC 全体を統一的にガバナンスしたい組織では Checkov、あるいは両方の併用が推奨されます。ルールのカバレッジが完全に一致するわけではないため、可能であれば両方を CI に組み込み、指摘の重複や差分を確認するのが安全です。

**Q2. スキャンで大量の警告が出て運用が回りません。どう対処すべきですか？**
A. まずは Critical/High レベルのみを CI のブロック条件にし、Medium/Low は警告表示に留めるところから始めます。既存コードに対しては、修正が難しい既知の指摘をベースライン(Checkov の `--baseline` オプションなど)として登録し、新規追加分から段階的に品質を上げていく方法が現実的です。

**Q3. tfsec は Trivy に統合されると聞きましたが、今後どうすればよいですか？**
A. Aqua Security は tfsec の機能を `trivy config`(IaC スキャン)に統合する方針を示しており、tfsec 単体は保守モードに移行しています。新規プロジェクトでは Trivy の IaC スキャン機能への移行を検討しつつ、既存の CI 設定はすぐに壊れるわけではないため、移行タイミングはチームのロードマップに合わせて計画的に進めれば問題ありません。
