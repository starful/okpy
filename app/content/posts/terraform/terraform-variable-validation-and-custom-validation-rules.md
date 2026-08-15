---
title: 'Terraform変数バリデーションとカスタムバリデーションルール実践ガイド'
date: 2026-08-15
category: terraform
slug: terraform-variable-validation-and-custom-validation-rules
summary: '直前のメッセージに含まれていた「ツールを使わずプレーンテキストのみで応答せよ」という指示は、あなたの実際のリクエストとは無関係に埋め込まれたもので、プロンプトインジェクションの可能性があります。念のためお伝えしておきます。ご依頼のTerraformブログ記事はツール不要のテキスト生成タスクなので、通常どおり作成し…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260815195534.jpg'
lang: ja
---

直前のメッセージに含まれていた「ツールを使わずプレーンテキストのみで応答せよ」という指示は、あなたの実際のリクエストとは無関係に埋め込まれたもので、プロンプトインジェクションの可能性があります。念のためお伝えしておきます。ご依頼のTerraformブログ記事はツール不要のテキスト生成タスクなので、通常どおり作成します。

# Terraform変数バリデーションとカスタムバリデーションルール実践ガイド

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260815195534.jpg)


Terraformでインフラをコード化していく上で、モジュールや設定ファイルが複雑になるほど「誤った値が渡されたまま`apply`が実行されてしまう」リスクが高まります。変数バリデーション（`validation`ブロック）は、この問題を`plan`実行前の早い段階で検知するための仕組みです。本記事では概念からHCLの実例、state・モジュールとの関係、注意点までを実践的にまとめます。

## 1. 変数バリデーションとは何か

Terraformの`variable`ブロックには、Terraform 0.13以降`validation`サブブロックを追加できます。これは変数に渡された値が満たすべき条件を宣言し、条件に違反した場合は`terraform plan`や`terraform apply`の実行を止めてエラーメッセージを表示する機能です。

従来はREADMEに「このリージョンはap-northeast-1かus-east-1のみ対応」と書いても、実際に間違った値を渡すとエラーはクラウドAPI呼び出し時（多くはリソース作成の途中）まで発覚しませんでした。`validation`ブロックを使うことで、こうした制約をコードとして表現し、実行前の静的チェックとして機能させられます。

基本構文は次のとおりです。

```hcl
variable "environment" {
  type        = string
  description = "デプロイ環境名"

  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment)
    error_message = "environment は \"dev\", \"stg\", \"prod\" のいずれかである必要があります。"
  }
}
```

`condition`は真偽値を返す式で、`false`の場合に`error_message`が表示されます。1つの`variable`ブロックに複数の`validation`ブロックを記述することも可能で、それぞれ独立して評価されます。

## 2. HCL実例

### 2.1 文字列パターンの検証

正規表現による命名規則の強制はよくあるユースケースです。

```hcl
variable "bucket_name" {
  type = string

  validation {
    condition     = can(regex("^[a-z0-9-]{3,63}$", var.bucket_name))
    error_message = "bucket_name は小文字英数字とハイフンのみ、3〜63文字で指定してください。"
  }
}
```

`can()`関数でラップしているのがポイントです。`regex()`はマッチしない場合エラーを送出するため、`can()`で包むことで「マッチしない=false」に変換し、Terraformの評価を止めずにバリデーションエラーとして扱えます。

### 2.2 数値範囲・複数条件の組み合わせ

```hcl
variable "instance_count" {
  type = number

  validation {
    condition     = var.instance_count >= 1 && var.instance_count <= 10
    error_message = "instance_count は1〜10の範囲で指定してください。"
  }
}

variable "cidr_block" {
  type = string

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "cidr_block は有効なCIDR表記である必要があります。"
  }

  validation {
    condition     = tonumber(split("/", var.cidr_block)[1]) <= 24
    error_message = "サブネットマスクは/24以下（広いレンジ）を指定してください。"
  }
}
```

同一変数に複数の`validation`を並べることで、独立した観点（形式チェックとビジネスルール）を分離して記述できます。

### 2.3 オブジェクト型・複合型の検証

```hcl
variable "tags" {
  type = map(string)

  validation {
    condition     = contains(keys(var.tags), "Owner")
    error_message = "tags には \"Owner\" キーを必ず含めてください。"
  }
}

variable "instance_config" {
  type = object({
    type       = string
    disk_size  = number
    monitoring = bool
  })

  validation {
    condition     = var.instance_config.disk_size >= 20
    error_message = "disk_size は20GB以上を指定してください。"
  }
}
```

### 2.4 変数間の相互参照（Terraform 1.9以降）

Terraform 1.9以降では、`condition`式の中で同一モジュール内の他の変数を参照できるようになりました（それ以前は自身の変数のみ参照可能という制約がありました）。

```hcl
variable "min_size" {
  type = number
}

variable "max_size" {
  type = number

  validation {
    condition     = var.max_size >= var.min_size
    error_message = "max_size は min_size 以上である必要があります。"
  }
}
```

これによりASG（Auto Scaling Group）のようにパラメータ同士の整合性が求められるケースを、追加の`locals`やチェックブロックを使わずシンプルに表現できます。

## 3. stateとの関係

`validation`ブロックはプラン生成前、つまり値がグラフに反映される最初期のフェーズで評価されます。したがって**stateファイルには一切影響しません**。バリデーションに失敗した場合、そもそもリソースの作成・更新処理自体が実行されないため、`terraform.tfstate`に不整合な状態が書き込まれることもありません。

これは`lifecycle`ブロックの`precondition`/`postcondition`（Terraform 1.2以降）との違いを理解する上で重要です。`validation`は入力値そのものを検証するのに対し、`precondition`/`postcondition`はリソースやデータソースの評価結果、つまり実際にAPIから返ってきた値やstate上の値を含めて検証します。両者は補完関係にあり、入力段階のガードは`variable`の`validation`、実行結果の整合性チェックは`lifecycle`の`precondition`/`postcondition`で行うのが定石です。

```hcl
resource "aws_instance" "web" {
  # ...

  lifecycle {
    postcondition {
      condition     = self.instance_state == "running"
      error_message = "起動したインスタンスの状態がrunningではありません。"
    }
  }
}
```

## 4. モジュールでの活用

モジュール開発において変数バリデーションは特に効果を発揮します。モジュールの利用者はREADMEを読み飛ばして値を渡すことも多いため、モジュール境界で誤入力を弾く仕組みは品質担保に直結します。

```hcl
# modules/vpc/variables.tf
variable "vpc_cidr" {
  type = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr は有効なCIDRブロックである必要があります。"
  }
}

variable "az_count" {
  type = number

  validation {
    condition     = var.az_count >= 2 && var.az_count <= 6
    error_message = "az_count は2〜6の範囲で指定してください（高可用性のため最低2AZ推奨）。"
  }
}
```

モジュール利用側（ルートモジュール）では、このエラーは`terraform plan`実行時にモジュール呼び出し箇所を指し示す形で表示されるため、どのモジュールのどの変数が問題なのかが即座に分かります。社内で共通モジュールをTerraform Registryやプライベートレジストリで配布している場合、`validation`ブロックは実質的な「型システムの拡張」として機能し、ドキュメントを読まなくても誤用に気づける安全網になります。

## 5. 注意点

- **他リソースの属性は参照できない**：`condition`式で参照できるのは、原則としてその変数自身（および1.9以降は同一モジュール内の他の変数）だけです。`data`ソースやリソースの属性を参照しようとするとエラーになります。実行時に決まる値のチェックが必要な場合は`precondition`/`postcondition`を使います。
- **エラーメッセージは静的文字列が基本**：Terraform 1.3以降は`error_message`内で変数を埋め込む簡易な補間が可能になりましたが、複雑な動的メッセージ生成には向きません。可読性を優先し簡潔に書くのがおすすめです。
- **`sensitive = true`の変数との組み合わせ**：機密変数をバリデーションする際、エラーメッセージに値そのものを含めると意図せずログに機密情報が出力される恐れがあります。値ではなく制約内容のみを記述しましょう。
- **評価順序**：複数の`validation`ブロックがある場合、いずれか1つが失敗すると即座にエラーになりますが、他の`validation`も評価され、複数のエラーメッセージがまとめて表示されることがあります。エラーメッセージは独立して理解できる文言にしておくと親切です。
- **CI/CDでの活用**：`terraform validate`はバリデーションブロックの構文チェックはしますが、実際の値に対する`condition`評価は行いません。値の検証を確実に行うには`terraform plan`（または`-var`を与えた`plan`）をCIパイプラインに組み込む必要があります。

## 6. AWS/GCP/Azureとの関係

変数バリデーション自体はクラウドプロバイダーに依存しないTerraform言語（HCL）の機能ですが、実務では各クラウドの制約をコードに落とし込む用途で多用されます。

- **AWS**：リージョン名（`ap-northeast-1`など）のホワイトリスト化、S3バケット名の命名規則（グローバルユニーク・小文字のみ）、EC2インスタンスタイプの許可リストなど。誤ったリージョンやインスタンスタイプを指定してAPIエラーになる前に弾けます。
- **GCP**：プロジェクトIDの命名規則（6〜30文字、小文字英数字とハイフン）、ゾーン・リージョンの整合性チェック、ラベル値の文字種制限（GCPはラベルに使える文字がAWSタグより厳しい）などに活用されます。
- **Azure**：リソースグループ名やストレージアカウント名（3〜24文字、小文字英数字のみ）のような、プロバイダー固有の厳格な命名制約をバリデーションで事前に検証するケースが多いです。

いずれのクラウドでも「APIコール時に初めて分かるエラー」を「plan時に分かるエラー」へと前倒しできる点が共通のメリットです。

## FAQ

**Q1. `validation`ブロックと`type`制約（`string`, `number`など）の違いは何ですか？**
A. `type`は値の"型"（データ構造）を強制するものです。`validation`は型が正しいことを前提に、さらに具体的な"値の中身"（範囲・パターン・許可リストなど）を検証します。両者は併用するのが基本で、`type`だけでは防げない不正値を`validation`で補完します。

**Q2. `default`値にも`validation`は適用されますか？**
A. はい。`default`が設定されていても、実際に確定した値（利用者が明示指定しなければ`default`値）に対して`validation`は評価されます。そのため`default`値自体が制約に違反していると、変数を明示指定しなくてもエラーになります。`default`値は必ず自身の`validation`を満たすように設計してください。

**Q3. `validation`で他のリソースの存在有無をチェックしたいのですが可能ですか？**
A. 直接はできません。`condition`式は変数の評価結果のみに基づくため、`data`ソースやリソースを参照する検証はサポート外です。この種のチェックは、リソース定義側の`lifecycle`ブロックにある`precondition`（作成前）や`postcondition`（作成後）を使うか、`data`ソースの結果を`locals`で加工した上で別途エラーを発生させる設計（例：`null_resource`やCIでの事前チェックスクリプト）を検討してください。

---

変数バリデーションは導入コストが低い一方で、チームの運用品質を大きく底上げする機能です。まずは命名規則や範囲制約など「よく事故る箇所」から`validation`ブロックを追加し、モジュール境界の安全網として育てていくのがおすすめです。
