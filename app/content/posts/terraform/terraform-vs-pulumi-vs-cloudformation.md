---
category: terraform
cover: https://storage.googleapis.com/ok-project-assets/okpy/2026072521492702.jpg
date: 2026-07-22
lang: ja
slug: terraform-vs-pulumi-vs-cloudformation
summary: インフラストラクチャをコードとして管理する「Infrastructure as Code（IaC）」は、現代のクラウドネイティブなシステム開発において不可欠なアプローチです。しかし、IaC
  ツールを選択する際、「標準的な Terraform を選ぶべきか」「プログラミング言語が使える Pulumi に移行すべきか…
title: 【2026年版】Terraform vs Pulumi vs CloudFormation 徹底比較・実践ガイド：IaC選定の決定版
---


# 【2026年版】Terraform vs Pulumi vs CloudFormation 徹底比較・実践ガイド：IaC選定の決定版

![cover](https://storage.googleapis.com/ok-project-assets/okpy/2026072521492702.jpg)


インフラストラクチャをコードとして管理する「Infrastructure as Code（IaC）」は、現代のクラウドネイティブなシステム開発において不可欠なアプローチです。しかし、IaC ツールを選択する際、「標準的な Terraform を選ぶべきか」「プログラミング言語が使える Pulumi に移行すべきか」「AWS 純正の CloudFormation で閉じるべきか」という悩みに直面するエンジニアやアーキテクトは少なくありません。

本記事では、技術ブログ「OKPy」の編集部が、現在主流である3大 IaC ツール**Terraform**、**Pulumi**、**CloudFormation**を網羅的に徹底比較します。基本概念から記述構文（HCL/TypeScript/YAML）、State（状態管理）の仕組み、モジュール化、運用上の注意点、AWS/GCP/Azure との関係性まで、実践的なコード例を交えて解説します。

---

## 1. 各IaCツールの基本概念と特徴

まずは、各ツールがどのような思想のもとで設計され、どのような特徴を持っているかを整理します。

### 1.1 Terraform：HCLによる宣言的プロビジョニングのグローバルスタンダード

HashiCorp 社によって開発された **Terraform** は、インフラ業界におけるデファクトスタンダード（事実上の標準）です。

*   **思想**: 独自のドメイン特化言語（DSL）である **HCL（HashiCorp Configuration Language）** を使用し、「あるべき状態」を宣言的に記述します。
*   **プロバイダーエコシステム**: AWS、GCP、Azure、Datadog、Cloudflare など、数千を超えるサービスに対応する「Provider」が存在し、マルチクラウド環境を一括管理できます。
*   **特徴**: 宣言型アプローチのため、コードを読むだけで現在のインフラ構成を理解しやすい利点があります。一方で、条件分岐や繰り返し処理といった複雑なロジックを記述する際には HCL 特有の制約に直面することがあります。

### 1.2 Pulumi：汎用プログラミング言語で記述する次世代IaC

**Pulumi** は、TypeScript、Python、Go、C#、Java といった既存のメジャーなプログラミング言語を用いてインフラを定義できるモダンな IaC ツールです。

*   **思想**: 開発者が普段使い慣れている言語の表現力、型システム、ループ処理、エコシステム（NPMやPyPIなど）をそのままインフラ定義に活用します。
*   **プロバイダー対応**: Terraform の Provider を変換して利用する仕組み（Bridge）に加え、Cloud Control API などを利用した Native Provider（AWS Native, Google Native など）も提供されています。
*   **特徴**: IF文やFORループ、クラス定義、抽象化、ユニットテストが容易に記述できます。一方で、プログラミング言語の自由度が高すぎるため、コードが乱雑化・複雑化しやすいというトレードオフが存在します。

### 1.3 CloudFormation：AWS純正のマネージドサービス

**AWS CloudFormation** は、AWS が公式に提供するネイティブなインフラ管理サービスです。

*   **思想**: JSON または YAML フォーマットを用いて、AWS リソースのスタックを定義・デプロイします。
*   **特徴**: AWS エンジン内で非同期に処理されるため、ローカルマシンにデプロイ実行環境を用意する必要がありません。AWS サービスの新機能への追従が早く、追加費用なし（リソース代金のみ）で利用可能です。
*   **制約**: 基本的に AWS 専用ツールであり、他社クラウド（GCPやAzure）の管理には適していません。また、YAML/JSON による記述は冗長になりがちで、大規模な定義ファイルは視認性が低下します。

---

## 2. AWS / GCP / Azure との関係性

マルチクラウド運用の視点から、各ツールが主要クラウドプロバイダー（AWS / GCP / Azure）とどのように連携するかを簡潔にまとめます。

| 項目 | Terraform | Pulumi | CloudFormation |
| :--- | :--- | :--- | :--- |
| **AWS** | 非常に強力（`hashicorp/aws`）<br>最新機能への追従も早い | 非常に強力（`pulumi-aws`, `pulumi-aws-native`） | **完全ネイティブ**（最優先サポート） |
| **GCP** | 非常に強力（`hashicorp/google`） | 強力（`pulumi-gcp`, `pulumi-google-native`） | 非対応（外部連携プラグイン等を除く） |
| **Azure** | 非常に強力（`hashicorp/azurerm`） | 強力（`pulumi-azure`, `pulumi-azure-native`） | 非対応 |
| **マルチクラウド統合** | **同一コードベースで一括管理可能** | **同一コードベース・同一言語で管理可能** | AWS 単体に限定される |

**ポイント**:
AWS のみに閉じたプロジェクトであれば CloudFormation（または AWS CDK）が最も手軽ですが、将来的に GCP や Azure、あるいは SaaS（Datadog や PagerDuty など）も含めた統合管理を行う場合は、Terraform または Pulumi の導入が必須となります。

---

## 3. 構文・記述比較（HCL vs TypeScript vs YAML）

実際のコード例で比較を行うため、**「AWS 上に VPC、パブリックサブネット、および S3 バケットを作成する」** という共通の構成を各ツールで記述します。

### 3.1 Terraform (HCL) の実装例

```hcl
# main.tf
terraform {
  required_version = ">= 1.5.0"
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

# VPCの作成
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "okpy-terraform-vpc"
  }
}

# サブネットの作成
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-northeast-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "okpy-terraform-public-subnet"
  }
}

# S3バケットの作成
resource "aws_s3_bucket" "storage" {
  bucket = "okpy-example-bucket-tf-2026"

  tags = {
    Environment = "Production"
  }
}

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "Created VPC ID"
}
```

### 3.2 Pulumi (TypeScript) の実装例

```typescript
// index.ts
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

// VPCの作成
const vpc = new aws.ec2.Vpc("okpy-pulumi-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    enableDnsSupport: true,
    tags: {
        Name: "okpy-pulumi-vpc",
    },
});

// サブネットの作成
const publicSubnet = new aws.ec2.Subnet("okpy-pulumi-public-subnet", {
    vpcId: vpc.id, // リソース間の参照を直接オブジェクトプロパティで記述
    cidrBlock: "10.0.1.0/24",
    availabilityZone: "ap-northeast-1a",
    mapPublicIpOnLaunch: true,
    tags: {
        Name: "okpy-pulumi-public-subnet",
    },
});

// S3バケットの作成
const bucket = new aws.s3.Bucket("okpy-example-bucket-pulumi-2026", {
    tags: {
        Environment: "Production",
    },
});

// アウトプットのエクスポート
export const vpcId = vpc.id;
export const bucketName = bucket.id;
```

### 3.3 CloudFormation (YAML) の実装例

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'OKPy CloudFormation Example - VPC and S3'

Resources:
  # VPCの作成
  MainVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: okpy-cfn-vpc

  # サブネットの作成
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MainVPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: ap-northeast-1a
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: okpy-cfn-public-subnet

  # S3バケットの作成
  StorageBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: okpy-example-bucket-cfn-2026
      Tags:
        - Key: Environment
          Value: Production

Outputs:
  VpcId:
    Description: 'Created VPC ID'
    Value: !Ref MainVPC
```

### 3.4 記述構文の比較と考察

1.  **可読性と宣言性**:
    *   **Terraform (HCL)**: 構造化されており、どのようなリソースが作成されるかが直感的に理解しやすい設計です。
    *   **Pulumi (TypeScript)**: TypeScript の静的型チェック（IntelliSense 等）が強力に効くため、IDE 上でドキュメントを参照しながら補完入力できます。
    *   **CloudFormation (YAML)**: 階層構造が深くなるとインデントエラーが発生しやすく、文字数が増加する傾向にあります。

2.  **ロジック・制御構造**:
    *   **Terraform**: `count` や `for_each` を使用しますが、高度な条件分岐や複雑なデータ加工には `dynamic` ブロックやビルトイン関数を組み合わせる必要があり、構文が煩雑化しがちです。
    *   **Pulumi**: `if` 文や `Array.map()` などの標準的な言語機能をそのまま活用でき、複雑な処理を簡潔に書くことができます。
    *   **CloudFormation**: `Fn::If` や `Fn::Equals` などの組込み関数を利用しますが、複雑な条件指定は可読性を著しく低下させます。

---

## 4. State（状態管理）のアーキテクチャ比較

IaC ツールを実運用するうえで最も重要なテーマの一つが「**State（状態管理）**」です。IaC は「コード上の定義」と「実際のクラウド上のリソース」のマッピングを維持するために State を必要とします。

```
[ コード定義 ] <---> [ State (状態管理) ] <---> [ 実際のクラウドリソース ]
```

### 4.1 Terraform の State 管理

*   **仕組み**: `terraform.tfstate` という JSON ファイルに、管理対象のリソース ID や属性情報を保持します。
*   **バックエンド構造**:
    *   チーム開発では、S3 バケットなどの遠隔ストレージ（Remote Backend）に State ファイルを配置します。
    *   **排他制御（State Locking）**: 複数人が同時にデプロイを実行して State が破損するのを防ぐため、AWS では **DynamoDB テーブル** などを用いてロックを取得します。
*   **特徴**: State が実際の環境と乖離した場合は、`terraform refresh` や `terraform import`、`terraform state rm` などのコマンドで手動で整合性を保つ必要があります。

### 4.2 Pulumi の State 管理

*   **仕組み**: Pulumi も Terraform と同様に State 概念（Checkpoint File）を持ちます。
*   **デフォルト構成（Pulumi Service）**:
    *   標準では Pulumi 社が提供する SaaS 型のマネージドサービス「**Pulumi Service (Pulumi Cloud)**」がバックエンドとして利用されます。
    *   ログイン認証、State の暗号化保存、履歴追跡、排他ロック、Web UI でのグラフィカルな表示が最初から提供されます。
*   **Self-Managed Backend**:
    *   セキュリティ規定により SaaS が利用できない場合、AWS S3、Google Cloud Storage、Azure Blob Storage などを直接バックエンドとして指定することも可能です（ただし、ロック処理などを自前で考慮する必要があります）。

### 4.3 CloudFormation の状態管理

*   **仕組み**: CloudFormation にはローカルやユーザー指定ストレージに置く「State ファイル」が存在しません。
*   **完全マネージド**:
    *   AWS のバックエンドエンジンが「スタック（Stack）」単位でリソースの状態を裏側で自動管理します。
    *   ユーザーは State のロック処理やファイル破損のリスクを意識する必要がありません。
*   **ドリフト検出（Drift Detection）**:
    *   マネジメントコンソールや CLI から「ドリフト検出」を実行することで、テンプレートの定義と手動変更されたリソースの差分をチェックできます。

---

## 5. モジュール化・再利用性の比較

設計の共通化やテンプレート化を行うための「モジュール機構」について比較します。

### 5.1 Terraform：Module

Terraform ではディレクトリ単位でリソース群をまとめ、**Module** としてカプセル化できます。

```hcl
# モジュールの呼び出し側 (main.tf)
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr = "10.0.0.0/16"
  env      = "production"
}
```

*   **レジストリ**: HashiCorp が運営する「Terraform Registry」には、AWS / GCP / Azure のベストプラクティスに沿った公式・サードパーティ製モジュールが多数公開されています。
*   **再利用性**: 構成が固定化されているため安全性が高い反面、汎用性を高めようとするとパラメータ（`variable`）が大量に増加する傾向があります。

### 5.2 Pulumi：ComponentResource と Package

Pulumi では、クラスの継承や組み込み機能を用いて独自のリソースコンポーネントを作成できます。

```typescript
// 自作コンポーネントリソースの例
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

interface SecureBucketArgs {
    bucketName: string;
}

export class SecureBucket extends pulumi.ComponentResource {
    public readonly bucket: aws.s3.Bucket;

    constructor(name: string, args: SecureBucketArgs, opts?: pulumi.ComponentResourceOptions) {
        super("custom:x:SecureBucket", name, {}, opts);

        this.bucket = new aws.s3.Bucket(name, {
            bucket: args.bucketName,
            acl: "private",
            serverSideEncryptionConfiguration: {
                rule: {
                    applyServerSideEncryptionByDefault: {
                        sseAlgorithm: "AES256",
                    },
                },
            },
        }, { parent: this });

        this.registerOutputs({
            bucketName: this.bucket.id,
        });
    }
}
```

*   **パッケージ配布**: 作成したコンポーネントは、NPM パッケージや PyPI パッケージとして自社のプライベートリポジトリで配布・共有できます。ソフトウェア開発の標準的なライブラリ管理手法をそのまま導入できる点が強みです。

### 5.3 CloudFormation：Nested Stacks / Modules / AWS CDK

*   **Nested Stacks (入れ子スタック)**: `AWS::CloudFormation::Stack` リソースを使って他のテンプレートを呼び出します。テンプレート間での親子の依存関係やパラメータの引き継ぎが煩雑になりがちです。
*   **CloudFormation Modules**: リソース定義をフラグメント化して共有する仕組みですが、普及度は限定的です。
*   **AWS CDK（Cloud Development Kit）**:
    *   CloudFormation の抽象化レイヤーとして標準的に使われているのが **AWS CDK** です。
    *   TypeScript や Python 等で記述し、最終的に CloudFormation YAML を生成（Synthesize）してデプロイします。CloudFormation 直書きの難点を補う強力な選択肢となっています。

---

## 6. 実践における注意点・アンチパターン

導入・運用時に陥りやすい注意点やリスクについて説明します。

### 6.1 ライセンス問題と Terraform / OpenTofu の文脈

2023年8月、HashiCorp 社は Terraform のライセンスをオープンソース（MPL 2.0）から **BSL 1.1（Business Source License）** に変更しました。

*   **インパクト**: 通常のインフラ構築・運用を行う企業ユーザーへの直接的な影響は軽微ですが、Terraform と競合する商業サービス（競合 SaaS など）を提供している企業は利用制限を受ける可能性があります。
*   **OpenTofu への分岐**: このライセンス変更を受け、Linux Foundation のもとで完全オープンソースのフォークプロジェクトである **OpenTofu** が誕生しました。現在、Terraform と互換性を保ちながら独立して開発が進められています。
*   **選定時の注意点**: オープンソースに強いこだわりがある組織では、Terraform ではなく OpenTofu や Pulumi を選定するケースが増加しています。

### 6.2 Pulumi の「プログラミング言語が使える」リスク

Pulumi の最大の強みである「汎用言語が使える」という点は、運用上のリスクにもなり得ます。

*   **アンチパターン: 複雑すぎるロジックの混入**:
    *   インフラコード内で外部 API を叩く、複雑な算術計算を行う、DB からデータを取得して動的に構築を変更する、といった過剰なプログラミングを行うと、コードの再現性や予測可能性が低下します。
*   **技術負債化**:
    *   インフラエンジニアとアプリケーションエンジニアで言語の習熟度にギャップがある場合、特定のメンバーしかメンテナンスできない「ブラックボックスコード」が発生しやすくなります。

### 6.3 CloudFormation のデプロイ速度とロールバックの挙動

*   **デプロイの遅さ**: CloudFormation は AWS のキューイングシステムを介してリソース生成を行うため、Terraform や Pulumi と比較してデプロイ完了までに時間がかかる傾向があります。
*   **ロールバックの失敗地獄**:
    *   リソース作成途中でエラーが発生した場合、自動ロールバックが試行されます。
    *   しかし、削除順序の不整合や依存関係の残りによって「ロールバック自体が失敗する（`UPDATE_ROLLBACK_FAILED`）」状態に陥ると、マネジメントコンソールからリソースを手動削除して状態を復旧させる手間が発生します。

---

## 7. 選定チャート・比較マトリクス

どのツールを採用すべきか迷った際の判断指標として、選定チャートと総合比較マトリクスを用意しました。

### 7.1 選定フローチャート

```
[IaCツールの選定]
   |
   +---> 主な対象クラウドは AWS のみか？
   |        |
   |        +-- (Yes) --> プログラミング言語で書きたいか？
   |        |                |
   |        |                +-- (Yes) --> AWS CDK (CloudFormationベース)
   |        |                +-- (No)  --> CloudFormation または Terraform
   |        |
   |        +-- (No: マルチクラウド/SaaS連携あり)
   |                 |
   +-----------------+
   |
   +---> 開発メンバーのスキルセットと運用方針は？
            |
            +-- 汎用言語（TS/Python等）の型安全性を活かしたい / アプリエンジニア主体
            |     --> Pulumi
            |
            +-- 宣言的で読みやすく、業界の標準ナレッジを活用したい / SRE・インフラ専門チーム主体
                  --> Terraform (または OpenTofu)
```

### 7.2 総合比較マトリクス

| 評価項目 | Terraform | Pulumi | CloudFormation |
| :--- | :--- | :--- | :--- |
| **学習コスト** | 中（HCLの習得が必要） | 低〜中（既存言語を利用可能） | 中〜高（YAML構造と独自の記法） |
| **マルチクラウド対応** | **極めて高い** | **極めて高い** | 不可（AWS専用） |
| **コードの抽象化・再利用** | 中（Module構造） | **極めて高い**（クラス・ライブラリ化） | 低（CDK利用で高） |
| **デプロイ速度** | **速い**（並列処理） | **速い**（並列処理） | やや遅い |
| **State管理の手間** | 手動設定が必要（S3/DynamoDB） | 標準で SaaS（自前設定も可） | **不要**（完全マネージド） |
| **エコシステム・情報量** | **圧倒的** | 増加傾向 | 豊富（AWS領域） |
| **ライセンス** | BSL 1.1（商用利用注意） | Apache 2.0 | AWS利用規約 |

---

## 8. よくある質問（FAQ） 3件

### Q1. Terraform から Pulumi への移行は現実的に可能ですか？

**A. 十分に可能です。**
Pulumi には Terraform の既存構成をスムーズに移行するためのエコシステムが用意されています。

1.  **既存リソースの取り込み**:
    `pulumi import` コマンドを使用することで、すでにデプロイ済みのクラウドリソースを Pulumi の State と TypeScript/Python コードとして自動生成・取り込みできます。
2.  **`pulumi-converter` / `tf2pulumi` ツール**:
    既存の `.tf` ファイル（HCL）を読み込み、指定した言語（TypeScript など）の Pulumi コードに自動変換するコンバーターツールが提供されています。

段階的にリソースを移行する場合は、Terraform の State を Pulumi 側から参照する `pulumi-terraform` プロバイダーを利用し、境界を区切りながら順次リソースを移管していく戦略が有効です。

### Q2. AWS CDK と CloudFormation、Pulumi は何が違うのですか？

**A. 抽象化のレイヤーと、バックエンドのデプロイエンジンが異なります。**

*   **AWS CDK**:
    プログラミング言語（TypeScriptやPython等）で記述しますが、実行時にコードを**CloudFormation テンプレート（YAML/JSON）へコンパイル（Synthesize）**します。実際のデプロイ処理は AWS 上の CloudFormation エンジンが担当します。
*   **Pulumi**:
    CloudFormation テンプレートを経由せず、プログラムの実行結果から直接 **AWS API（または Cloud Control API）を呼び出して**リソースを操作します。
*   **CloudFormation (直接記述)**:
    コンパイル手順を踏まず、YAML/JSON を直接スタックとして AWS にデプロイします。

「AWS 専用でよい・プログラミング言語を使いたい」場合は **AWS CDK**、「マルチクラウドで汎用言語を使いたい」場合は **Pulumi** が選択肢となります。

### Q3. Terraform のライセンス変更（BSL）に伴い、新規プロジェクトでは OpenTofu を選ぶべきですか？

**A. 自社のビジネスモデルとコンプライアンス要件によります。**

*   **クラウドインフラを社内用に構築する一般的な企業やスタートアップ**:
    BSL ライセンス下でも Terraform を無料で商用利用・運用できます。既存のエコシステムやドキュメントの量を重視するなら、依然として **Terraform** が第一選択肢になります。
*   **Terraform を自社 SaaS の裏側に組み込んでエンドユーザーに提供するようなサービス開発**:
    競合ライセンス条項に抵触するリスクがあるため、完全オープンソース（Linux Foundation 管理）である **OpenTofu** または **Pulumi** を選択することを強く推奨します。

なお、OpenTofu は Terraform 1.5/1.6 と高い互換性を持っているため、まず Terraform で構築し、必要に応じて OpenTofu へ切り替えるといった運用も技術的には容易です。

---

## 9. まとめ

本記事では、Terraform、Pulumi、CloudFormation の3大 IaC ツールについて多角的に徹底比較しました。

*   **Terraform**: 宣言的な HCL による**マルチクラウド管理の絶対的デファクトスタンダード**。圧倒的なドキュメント量と安定した実績を重視する場合に最適。
*   **Pulumi**: 汎用言語の表現力と型安全性を活かした**次世代 IaC**。複雑なロジック処理が必要な環境や、アプリケーション開発者がインフラも兼任するチームに最適。
*   **CloudFormation (および AWS CDK)**: AWS に特化した**フルマネージドで安全な統合環境**。State 管理の手間を省き、AWS エコシステムに特化したい場合に最適。

それぞれのツールが持つ思想やアーキテクチャの違いを正しく理解し、自社チームのスキルセットや対象インフラの規模・マルチクラウド要件に合わせた最適な IaC ツールを選定してください。
