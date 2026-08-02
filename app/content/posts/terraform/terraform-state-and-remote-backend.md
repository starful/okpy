---
category: terraform
cover: https://storage.googleapis.com/ok-project-assets/okpy/2026072521493804.jpg
date: 2026-07-25
lang: ja
slug: terraform-state-and-remote-backend
summary: Infrastructure as Code（IaC）ツールとして広く普及しているTerraformにおいて、最も重要でありながら事故やトラブルの原因になりやすいのが**State（ステート）の管理**です。
  1人でコードを書いている段階では「ローカルに生成される `terraform.tfstate`」だけで動…
title: 【Terraform】State管理とRemote Backend完全攻略ガイド：安全なチーム開発と運用ベストプラクティス
---


# 【Terraform】State管理とRemote Backend完全攻略ガイド：安全なチーム開発と運用ベストプラクティス

![cover](https://storage.googleapis.com/ok-project-assets/okpy/2026072521493804.jpg)


Infrastructure as Code（IaC）ツールとして広く普及しているTerraformにおいて、最も重要でありながら事故やトラブルの原因になりやすいのが**State（ステート）の管理**です。

1人でコードを書いている段階では「ローカルに生成される `terraform.tfstate`」だけで動作するため、Stateの重要性に気づきにくいかもしれません。しかし、チームでインフラを管理し始めたり、本番環境の構築・運用を行ったりする局面では、Stateの集中管理と排他制御（ロック）を提供する **Remote Backend（リモートバックエンド）** の導入が絶対に不可欠となります。

本稿では、Terraform編集部「OKPy」の視点から、Terraform Stateの基礎概念からRemote Backendの設定手順（AWS / GCP / Azure）、モジュール運用におけるStateの切り分け、事故を防ぐ運用ベストプラクティス、そして現場でよく直面するFAQまでを徹底的に解説します。

---

## 1. Terraform State（ステート）の基本概念と仕組み

### Stateとは何か？
TerraformにおけるState（ステート）とは、**「コード（.tfファイル）上に定義されたリソース」と「実際にクラウド上に存在するリソース」を紐付けるマッピング情報（メタデータ）** を保持するファイル（デフォルトでは `terraform.tfstate`）です。

Terraformは宣言型の言語です。`terraform apply` を実行した際、Terraformは「現在の状態」と「コード上のコード（あるべき状態）」を比較し、差分（Diff）を計算して必要なAPIリクエストを発行します。このとき「現在の状態」を瞬時に把握するために参照されるのがStateファイルです。

### なぜStateが必要なのか？
「クラウドのAPI（Describe / Listなど）を都度叩けば、ファイルなど作らなくても現在の状態がわかるのではないか？」という疑問を持つ方もいるかもしれません。TerraformがStateを必要とする主な理由は以下の3点です。

1. **リアルワールドリソースとのIDマッピング**
   例えば、HCLで `resource "aws_instance" "web" {}` と書いた際、それがAWS上のどの `i-0123456789abcdef0` に対応するのかという情報は、State内部に保存されています。
2. **依存関係の追跡**
   Terraformはリソース間の依存関係を追跡します。削除や変更の順番を正しく制御するために、既存の構成グラフをState内に保持しています。
3. **パフォーマンスの向上**
   大規模なインフラでは、毎回何百ものAPIコールをクラウドプロバイダーに送信すると `terraform plan` に膨大な時間がかかります。Stateがあることで、ローカルでのキャッシュや高速な差分計算が可能になります。

### `terraform.tfstate` の内部構造
`terraform.tfstate` は単なるJSONファイルです。以下はシンプルな構成のState例です。

```json
{
  "version": 4,
  "terraform_version": "1.7.0",
  "serial": 12,
  "lineage": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "outputs": {},
  "resources": [
    {
      "mode": "managed",
      "type": "aws_s3_bucket",
      "name": "example",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [
        {
          "schema_version": 0,
          "attributes": {
            "arn": "arn:aws:s3:::my-okpy-tfstate-bucket",
            "bucket": "my-okpy-tfstate-bucket",
            "id": "my-okpy-tfstate-bucket",
            "tags": {
              "Environment": "Dev"
            }
          },
          "sensitive_attributes": []
        }
      ]
    }
  ]
}
```

### ローカル管理（Local State）の危険性と限界
デフォルトのローカルState運用（自分の PC 上に `terraform.tfstate` を置いたまま開発すること）には、チーム開発・本番運用において決定的な欠点があります。

- **デッドロック・上書き（競合）**：複数のメンバーが同時に `apply` を実行すると、相手の更新を上書きしてインフラが破壊される。
- **データ紛失**：PCの故障や誤削除でStateが失われると、コードと実インフラの紐付けが切れ、最悪の場合再作成が必要になる。
- **機密情報の漏洩**：StateファイルにはDBの初期パスワードやSecret Keyなどのセンシティブな情報が**プレーンテキスト**で記録されます。Gitリポジトリに誤ってコミットすると致命的なセキュリティ事故に繋がります。

これらの課題を一挙に解決するのが **Remote Backend** です。

---

## 2. Remote Backend（リモートバックエンド）とは

Remote Backendとは、Stateファイルをローカルディスクではなく、クラウドストレージなどの遠隔ストレージに安全に保管し、管理する仕組みです。

```
【ローカル環境 / CI/CD】                【Remote Backend】
  Developer A  ──(apply)──┐             ┌────────────────────────┐
                         ├── Lock/Sync ─┤ Cloud Storage          |
  Developer B  ──(apply)──┘             | (S3 / GCS / Azure Blob)|
                                        │ + Lock DB (DynamoDB)   │
                                        └────────────────────────┘
```

### Remote Backendが提供する主要機能
1. **ステートの中央集権化（State Storage）**
   チーム全員、およびCI/CDパイプライン（GitHub Actions, GitLab CIなど）が常に「最新かつ単一の正しいState」を参照できます。
2. **排他制御（State Locking）**
   誰かが `terraform plan` や `apply` を実行している間、Stateを「ロック」します。他のメンバーの同時実行を弾くことで、二重更新によるクラッシュを防ぎます。
3. **自動暗号化とアクセス制御（Encryption & IAM）**
   ストレージの暗号化機能（SSE-KMSなど）を利用してState内の機密情報を保護できます。また、IAMポリシーでStateにアクセスできるユーザーやロールを制限できます。
4. **バージョニング（Versioning）**
   クラウドストレージのバージョニング機能を有効にすることで、万が一Stateが壊れたり誤操作で消去されたりした場合でも、過去の正常な状態に一瞬でロールバック可能です。

---

## 3. Remote Backendの実装パターンとHCLコード例

主要パブリッククラウド（AWS、GCP、Azure）におけるRemote Backendの具体的なHCL定義方法を解説します。

### 3.1 AWS パターン（S3 + DynamoDB）
AWS環境では、Stateファイルの格納に **Amazon S3**、ステートロック（State Locking）の管理に **Amazon DynamoDB** を組み合わせるのが標準的かつ最も安定した構成です。

#### Terraform定義（`backend.tf`）
```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote Backend 設定
  backend "s3" {
    bucket         = "okpy-tfstate-prd-aws"
    key            = "network/terraform.tfstate"
    region         = "ap-northeast-1"
    encrypt        = true
    dynamodb_table = "okpy-tfstate-lock"
  }
}
```

*解説*:
- `bucket`: Stateを保存するS3バケット名。
- `key`: バケット内のオブジェクトパス（リポジトリやコンポーネントごとにユニークなパスを設定）。
- `encrypt`: `true` にすることで、S3オブジェクトのサーバーサイド暗号化（AES256/KMS）を強制。
- `dynamodb_table`: ロック状態を管理するDynamoDBテーブル名（プライマリキーとして `LockID` (String) が必要）。

---

### 3.2 GCP パターン（Google Cloud Storage: GCS）
GCP環境では **Google Cloud Storage（GCS）** を使用します。GCSはネイティブで強力なオブジェクトロック（排他制御）機能を持っているため、AWSのように別途データベース（DynamoDBなど）を用意する必要がありません。

#### Terraform定義（`backend.tf`）
```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Remote Backend 設定
  backend "gcs" {
    bucket      = "okpy-tfstate-prd-gcp"
    prefix      = "env/production/system"
  }
}
```

*解説*:
- `bucket`: GCSバケット名。
- `prefix`: バケット内のフォルダパスに相当するプレフィックス。設定されたパス配下に `default.tfstate` が保存されます。
- GCSバックエンドは標準で排他ロックに対応しているため、追加の設定なしで安全にロック処理が行われます。

---

### 3.3 Azure パターン（Azure Blob Storage）
Azure環境では **Azure Blob Storage** を使用します。Azure Blob StorageもGCSと同様、Blob Lease（リースメカニズム）を利用して自動的にステートロックが行われます。

#### Terraform定義（`backend.tf`）
```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  # Remote Backend 設定
  backend "azurerm" {
    resource_group_name  = "rg-okpy-tfstate-prd"
    storage_account_name = "stokpytfstateprd"
    container_name       = "tfstate"
    key                  = "production.terraform.tfstate"
  }
}
```

*解説*:
- `resource_group_name`: ストレージアカウントが存在するリソースグループ名。
- `storage_account_name`: Storage Account名。
- `container_name`: Blobコンテナ名。
- `key`: コンテナ内のファイル名。

---

### 3.4 バックエンドリソース自体の作成問題（鶏と卵問題）
リモートバックエンドを構築する際、「**BackendにするためのS3バケットやDynamoDBテーブル自体は、誰がどうやって作成するのか？**」という問題（鶏と卵問題）が生じます。

この問題のベストプラクティス手順は以下の通りです。

1. **ステップ1**: Backend用のS3/GCS/Azureストレージを作成するHCLを一旦「ローカルState」で書く（またはマネジメントコンソール/CLIコマンドで作成する）。
2. **ステップ2**: `terraform apply` を実行し、ストレージリソースを実際に作成する。
3. **ステップ3**: `backend.tf` にリモートバックエンドの設定を追加・有効化する。
4. **ステップ4**: `terraform init` を実行する。Terraformが「ローカルにあるStateをリモートバックエンドに移行（Migrate）しますか？」と尋ねてくるので `yes` と答える。

この手順を踏むことで、手作業でのミスを防ぎ、管理リソース自体のコード化も達成できます。

---

## 4. モジュール開発とStateの関係性

Terraformでインフラ規模が大きくなると、**モジュール分割** と **Stateの分割** をどのように設計するかが重要になってきます。

### 4.1 モノリシックState vs 分割State
すべてのインフラ（VPC、DB、アプリサーバー、DNSなど）を1つのState（1つの `terraform.tfstate`）で管理することを**モノリシックState**と呼びます。これは初期設計としては楽ですが、規模が大きくなると以下の問題を引き起こします。

- **`plan` / `apply` の低速化**: リソース数に比例して実行時間が数分〜数十分と肥大化する。
- **影響範囲の拡大（爆発半径: Blast Radius）**: アプリの1プロパティを変えたいだけなのに、誤って本番のデータベース（RDSなど）を削除・再作成してしまう事故が起こりやすくなる。

そのため、システム境界やライフサイクルに応じて **State（ディレクトリ）を分割する** ことがベストプラクティスです。

#### 推奨されるディレクトリ分割構成例
```text
my-infrastructure/
├── modules/               # 再利用可能なモジュール群（Stateを持たない）
│   ├── vpc/
│   └── rds/
└── environments/          # 各環境・領域ごとのTerraformルートモジュール
    ├── prod/
    │   ├── 00_base/       # IAM, KMS など（変更頻度：低）
    │   ├── 10_network/    # VPC, Subnet, RouteTable（変更頻度：低）
    │   └── 20_app/        # ECS, ALB, AutoScaling（変更頻度：高）
    └── dev/
        ...
```

それぞれのディレクトリ（例: `00_base`, `10_network`, `20_app`）ごとに独自の `backend.tf` を定義し、独立したStateを持たせます。

### 4.2 モジュール内でのBackend定義のNGパターン
Terraformモジュール（`modules/vpc` など）を作成する際、**モジュール内部のHCLコードに `backend` ブロックを記述してはいけません。**

Backendの定義（保存先のバケット名やキー名など）は、**呼び出し元のルートモジュール（Root Module）** でのみ行うべきです。子モジュール内に `backend` を書いてしまうと、そのモジュールの再利用性が完全に失われてしまいます。

### 4.3 `terraform_remote_state` データソースを活用した連携
Stateを分割すると、「`20_app` の設定から、`10_network` で作成した `vpc_id` や `subnet_id` を参照したい」という状況が発生します。これに対処するための手段が `terraform_remote_state` データソースです。

#### 参照される側（`10_network/outputs.tf`）
```hcl
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

output "private_subnet_ids" {
  value       = aws_subnet.private[*].id
  description = "List of Private Subnet IDs"
}
```

#### 参照する側（`20_app/main.tf`）
```hcl
# 別ディレクトリ（10_network）のStateを読み出す設定
data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = "okpy-tfstate-prd-aws"
    key    = "network/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

# 読みだしたStateのoutputを利用してECSサービスを構築
resource "aws_ecs_service" "app" {
  name            = "okpy-web-app"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 2

  network_configuration {
    subnets         = data.terraform_remote_state.network.outputs.private_subnet_ids
    security_groups = [aws_security_group.app.id]
  }
}
```

※最近の設計プラクティスでは、`terraform_remote_state` は強力な依存関係（結合）を生むため、システム規模によっては **SSM Parameter Store** や **AWS Secrets Manager** などの外部キーバリューストアを経由して渡す設計も広く採用されています。

---

## 5. 運用時の注意点とアンチパターン

チーム運用で落とし穴にはまらないための重要ポイントを整理します。

### 5.1 暗号化とアクセス制御（機密情報の保護）
Stateファイルには、例えば `aws_db_instance` リソースを作成した際の `password` プロパティなどが、**暗号化されずにそのままのプレーンテキスト**で保存されます。

これを防ぐ・最小化するために以下のルールを徹底してください。
- **S3 / GCS / Azure Blob 側のバケット暗号化（KMS等）を必須にする**
- **バケットへのアクセス権限（IAM / RBAC）を最小権限にする**（例：一般開発者にはState読取専用、CI/CDパイプラインにのみ書込権限を付与する）
- **`.gitignore` に `*.tfstate` や `*.tfstate.backup` を必ず記述する**（誤コミット防止）

### 5.2 ステート管理用CLIコマンド（救援・修正用）
インフラのリネームや手動での設定変更を行った際、Stateと実インフラに不整合が生じることがあります。ファイルを直接手で編集する（JSONを壊す原因になる）のではなく、必ず専用の `terraform state` コマンド群を使用してください。

| コマンド | 用途・説明 |
| :--- | :--- |
| `terraform state list` | 現在のStateで管理されている全リソースの一覧を表示する |
| `terraform state show <RESOURCE>` | 特定のリソースのState内部の詳細情報を表示する |
| `terraform state mv <SRC> <DST>` | HCLコード上のリソース名を変更した際、破壊・再作成を防ぐためにState内の名前を変更する |
| `terraform state rm <RESOURCE>` | 実インフラを削除せず、Terraformの管理対象外（Stateからのみ除外）にする |
| `terraform state pull` | Remote Backendにある現在のStateを標準出力（JSON）に吐き出す |
| `terraform state push` | ローカルのStateファイルの内容をRemote Backendに強制書き込みする（非常に危険） |

#### コマンド使用例：リソース名の変更（`state mv`）
コード上で `aws_instance.web` を `aws_instance.app` に変更した場合、そのまま `apply` すると「古いサーバーを削除して新しいサーバーを作成」しようとします。これを防ぐために以下のコマンドを実行します。

```bash
$ terraform state mv aws_instance.web aws_instance.app
Move "aws_instance.web" to "aws_instance.app"
Successfully moved 1 object(s).
```

### 5.3 バックエンドの移行手順（`terraform init -migrate-state`）
ローカルからRemote Backendへ移行する際、あるいはRemote Backendの保存先S3バケットやキーを変更する際は、単にコードを書き換えた後に以下のコマンドを実行します。

```bash
$ terraform init -migrate-state
```

実行すると、古いBackendから新しいBackendへStateデータを自動的に転送・同期してくれます。既存のStateデータを破棄して新規作成し直したい場合のみ `-reconfigure` オプションを使いますが、事故を防ぐため通常は `-migrate-state` を利用してください。

---

## 6. よくある質問（FAQ）

### FAQ 1: `terraform.tfstate` を Git リポジトリのコミット対象にしてはいけない理由は何ですか？

**回答:**
主に以下の3つの深刻な問題が発生するためです。

1. **セキュリティリスク**: Stateファイルにはパスワード、APIキー、SSH秘密鍵、データベースの初期資格情報などがプレーンテキストで記録されます。Gitにコミットすると、閲覧権限を持つ全員に秘密情報が露出します。
2. **コンフリクトの頻発**: チームで開発している場合、開発者Aと開発者Bがそれぞれ `apply` を実行するとStateファイルが競合（Conflict）します。JSON形式の競合解消は困難を極め、手動マージは高確率でStateを破壊します。
3. **ロック機構の欠如**: Git自体には実行時の排他制御（同時実行の阻止）機能がないため、二重 `apply` によるクラウド側のインフラ破壊を防げません。

---

### FAQ 2: Remote Backend設定（`backend "s3"` 等）の中で変数（`var.xxx`）が使えないのはなぜですか？対処法はありますか？

**回答:**
Terraformの仕様上、`backend` ブロックはTerraformが変数の評価やモジュールの初期化を行う**前**（最も初期の段階）に評価されるため、HCL内の `variable` や `local` を参照することができません。

#### 対処法：バックエンドの動的設定（Partial Configuration）
`backend` ブロック内には静的な最小限の記述（または空記述）のみを行い、環境ごとの差分パラメータを `terraform init` 実行時に外部ファイルや引数から注入します。

**1. `backend.tf` の記述（共通部分）**
```hcl
terraform {
  backend "s3" {}
}
```

**2. 環境ごとの設定ファイルを用意（`config/prd.tfbackend`）**
```hcl
bucket         = "okpy-tfstate-prd-aws"
key            = "app/terraform.tfstate"
region         = "ap-northeast-1"
dynamodb_table = "okpy-tfstate-lock"
```

**3. 初期化コマンドでファイルを渡す**
```bash
$ terraform init -backend-config=config/prd.tfbackend
```
この方法を使えば、同一のHCLコードを利用しながら、環境（stg / prd）ごとに保存先バケットを柔軟に変更できます。

---

### FAQ 3: `Error locking state` でステートロックが解除できなくなった場合の安全な解除方法は？

**回答:**
`apply` の途中でネットワークが切断されたり、CI/CDジョブが強制的・異常終了（SIGKILLなど）したりすると、DynamoDBやGCS上の「ロック情報」が残ったままになり、次回以降以下のエラーが発生して実行できなくなることがあります。

```text
Error: Error acquiring the state lock: ConditionalCheckFailedException: ...
Lock Info:
  ID:        e1234567-89ab-cdef-0123-456789abcdef
  Path:      my-bucket/terraform.tfstate
  Operation: OperationTypeApply
  Who:       user@hostname
  Created:   2024-03-20 10:00:00.000000000 +0000 UTC
```

#### 解除手順:
1. **プロセスが本当に停止しているか確認**: 同僚やCI/CDパイプラインが「現在進行形」で `apply` を実行していないかをチャットツール等で必ず確認します（実行中のロック解除はState破壊に繋がります）。
2. **`force-unlock` コマンドの実行**: エラーメッセージに表示された **`Lock ID`** を指定してロックを強制解除します。

```bash
$ terraform force-unlock e1234567-89ab-cdef-0123-456789abcdef
Do you really want to force-unlock?
  Terraform will remove the lock on the remote state.
  This can damage the state if another process is running.

  Enter a value: yes

Terraform state has been successfully unlocked.
```

---

## 7. まとめ

Terraform StateとRemote Backendの適切な理解と設計は、Terraform運用の成功を左右する最も重要な土台です。

本ガイドの要点を再確認しましょう。

- **Stateはインフラの命**: 実リソースとHCLコードを繋ぐ重要ファイルであり、ローカルでの運用やGit管理は厳禁。
- **Remote Backendの導入**: AWS（S3+DynamoDB）、GCP（GCS）、Azure（Blob）それぞれの特性に合わせたRemote Backendを設定し、**暗号化**・**バージョニング**・**自動ロック**を有効化する。
- **適切な領域分割**: 大規模なインフラではディレクトリを細分化し、影響半径（Blast Radius）を小さく抑える。
- **安全な運用コマンド**: Stateの操作は手動修正を避け、必ず `terraform state` サブコマンド（`mv`, `rm` など）を使用する。

安全で堅牢なTerraform環境を構築し、ストレスのない快適なチーム開発を実現しましょう！
