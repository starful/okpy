---
title: 'Terraform testing strategies with Terratest 実践ガイド'
date: 2026-08-11
category: terraform
slug: terraform-testing-strategies-with-terratest
summary: 'Terraform でインフラをコード化(IaC)すると、コードレビューやバージョン管理といったソフトウェア開発のプラクティスをインフラにも適用できるようになります。しかし、`terraform plan` や `terraform validate` だけでは「意図した通りにリソースが作成され、期待通りに動作す…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260811072108.jpg'
lang: ja
---

# Terraform testing strategies with Terratest 実践ガイド

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260811072108.jpg)


## はじめに

Terraform でインフラをコード化(IaC)すると、コードレビューやバージョン管理といったソフトウェア開発のプラクティスをインフラにも適用できるようになります。しかし、`terraform plan` や `terraform validate` だけでは「意図した通りにリソースが作成され、期待通りに動作するか」までは検証できません。そこで登場するのが Terratest です。Terratest は HashiCorp が公開している Go 言語のテストライブラリで、Terraform コードを実際にデプロイし、動作を検証したうえで自動的に破棄するという「本物の環境に対する統合テスト」を書けるようにしてくれます。本記事では Terratest を使ったテスト戦略の基本概念から、HCL・Go のサンプルコード、state の扱い、モジュール単位のテスト設計、注意点、そしてよくある質問までを解説します。

## Terratest とは何か

Terratest は AWS・GCP・Azure・Kubernetes など、さまざまなインフラをコードでテストするための Go 言語製オープンソースライブラリです。基本的な流れは次の通りです。

1. Go のテストコードから `terraform init` と `terraform apply` を実行し、実際にリソースをデプロイする
2. デプロイされたリソース(EC2 インスタンスの IP、S3 バケット名、Cloud Run の URL など)に対して HTTP リクエストや SDK 呼び出しを行い、期待した振る舞いになっているかを検証する
3. テスト終了時に `defer` で `terraform destroy` を呼び出し、リソースを確実に破棄する

Terraform の `plan` は「構文的に正しいか」「差分が意図通りか」を確認するものであり、実際にネットワーク到達性があるか、ロードバランサーが正しくヘルスチェックを通すか、といった「実行時の振る舞い」までは保証しません。Terratest はこのギャップを埋め、実際にクラウド上へデプロイしたうえでブラックボックス的に検証する点が最大の特徴です。

## なぜ Terraform のテストが必要か

インフラコードは一度書いたら終わりではなく、モジュールの再利用や変更が頻繁に発生します。特に以下のようなケースでテストの価値が高まります。

- 複数チームで共有する Terraform モジュール(VPC、IAM ロール、EKS クラスタなど)を公開・配布している
- モジュールの変更が既存の利用者に破壊的変更をもたらさないか確認したい
- CI/CD パイプラインにインフラのデプロイを組み込んでおり、リグレッションを自動検知したい
- セキュリティ設定(パブリックアクセスの禁止、暗号化の強制など)を継続的に担保したい

これらは `terraform validate` や `tflint` のような静的解析だけではカバーできず、実際にデプロイしてこそ検証できる領域です。

## テスト対象となる HCL の例

まずテスト対象となるシンプルな Terraform モジュールを用意します。ここでは AWS 上に S3 バケットを作成する最小構成のモジュールを例にします。

```hcl
# modules/s3_bucket/main.tf
variable "bucket_name" {
  type        = string
  description = "作成する S3 バケット名"
}

variable "environment" {
  type    = string
  default = "dev"
}

resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

output "bucket_arn" {
  value = aws_s3_bucket.this.arn
}

output "bucket_id" {
  value = aws_s3_bucket.this.id
}
```

このモジュールに対して「バケットが実際に作成されるか」「バージョニングが有効になっているか」を Terratest で検証していきます。

## Terratest による Go テストコードの例

Terratest のテストは Go の標準テストフレームワーク(`testing` パッケージ)の上に構築されます。典型的な構成は以下のようになります。

```go
// test/s3_bucket_test.go
package test

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/aws"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

func TestS3BucketModule(t *testing.T) {
	t.Parallel()

	uniqueID := "okpy-terratest-example"
	awsRegion := "ap-northeast-1"

	terraformOptions := &terraform.Options{
		TerraformDir: "../modules/s3_bucket",
		Vars: map[string]interface{}{
			"bucket_name": uniqueID,
			"environment": "test",
		},
	}

	// テスト終了時に必ず destroy を実行する
	defer terraform.Destroy(t, terraformOptions)

	terraform.InitAndApply(t, terraformOptions)

	bucketID := terraform.Output(t, terraformOptions, "bucket_id")
	assert.Equal(t, uniqueID, bucketID)

	// AWS SDK 経由で実際のバケット状態を検証する
	actualStatus := aws.GetS3BucketVersioning(t, awsRegion, bucketID)
	assert.Equal(t, "Enabled", actualStatus)
}
```

ポイントは以下の3つです。

- `defer terraform.Destroy` を `InitAndApply` の直後に書くことで、テストの途中で失敗してもリソースが残らないようにする
- `terraform.Output` で Terraform の出力値を取得し、Go 側でアサーションする
- Terratest の各クラウド用モジュール(`aws`、`gcp`、`azure`)を使って、Terraform の外側から実際のクラウド API を叩いて状態を検証する

`uniqueID` にはランダム文字列を含めることが推奨されます。Terratest には `random.UniqueId()` というヘルパーがあり、並列実行時のリソース名衝突を避けられます。

## state の扱いとテストにおける注意

Terratest はデフォルトでは一時的な作業ディレクトリを使ってローカルの state ファイルを生成します。本番運用で使っている S3 バックエンドや Terraform Cloud の state とは切り離して実行するのが基本方針です。理由は次の通りです。

- テスト用の state を本番の state と混在させると、誤って本番リソースを destroy してしまうリスクがある
- テストは並列実行されることが多く、同一 state を共有すると competing lock やリソース衝突が発生する
- CI 環境ごとに一時的な state を使い捨てにすることで、テスト実行の冪等性を保てる

実務では `TerraformDir` に渡すディレクトリをテスト専用のコピーにするか、`backend "local"` を使う一時構成に切り替えることが多いです。また、`terraform.Options` に `BackendConfig` を指定して、テスト実行時のみ異なる state キーやバケットを使う運用も可能です。CI 上で state のロック競合を避けるため、テストごとに一意な `bucket_name` や `workspace` を割り当てることが重要になります。

## モジュール単位でのテスト設計

大規模な Terraform コードベースでは、ルートモジュール全体を毎回デプロイしてテストするとコストと時間がかかりすぎます。そこで以下のようなテスト戦略の階層化が有効です。

1. **ユニットテストに近い検証**: `terraform plan` の出力を JSON 化し、Go や `terraform show -json` の結果をパースしてリソース属性を検証する。実際のデプロイを伴わないため高速。
2. **モジュール単体のインテグレーションテスト**: 上記の S3 バケット例のように、個別モジュールを単独でデプロイして検証する。依存が少なく、実行時間も比較的短い。
3. **エンドツーエンドテスト**: VPC・EKS・RDS など複数モジュールを組み合わせた本番相当の構成をデプロイし、実際のアプリケーションが動作するかまで確認する。実行コストが高いため、CI では夜間バッチやリリース前のみ実行することが多い。

また、Terratest には `test_structure` パッケージがあり、`SkipStageEnv` を使うことで「デプロイ済みの環境に対して検証だけを再実行する」といったステージ分割が可能です。これにより、デプロイに失敗した際のデバッグや、検証ロジックだけを繰り返し修正するサイクルを高速化できます。

```go
test_structure.RunTestStage(t, "deploy", func() {
    terraform.InitAndApply(t, terraformOptions)
})

test_structure.RunTestStage(t, "validate", func() {
    validateBucket(t, terraformOptions)
})

test_structure.RunTestStage(t, "destroy", func() {
    terraform.Destroy(t, terraformOptions)
})
```

## AWS・GCP・Azure との関係

Terratest はクラウドプロバイダーを問わず利用できる設計になっており、`modules/aws`、`modules/gcp`、`modules/azure` といったパッケージがそれぞれ用意されています。

- **AWS**: 最もエコシステムが充実しており、EC2、S3、RDS、EKS、Lambda などほぼ全ての主要サービスに対応するヘルパー関数があります。IAM ロールやセキュリティグループの検証にもよく使われます。
- **GCP**: `modules/gcp` パッケージで Compute Engine、GKE、Cloud Storage などの検証が可能です。GCP はプロジェクト単位の課金・権限管理がテスト設計に影響するため、テスト専用プロジェクトを用意する運用が一般的です。
- **Azure**: `modules/azure` パッケージがあり、Resource Group、VM、AKS などをカバーします。Azure はリソースグループ単位でのクリーンアップがしやすく、テスト後の後片付けがシンプルになる利点があります。

いずれのクラウドでも共通する注意点は、テスト用の認証情報(IAM ロールやサービスアカウント)を本番環境から分離し、最小権限で運用することです。CI 上で Terratest を実行する場合は、OIDC 連携などを使って長期的なシークレットを持たない認証方式を採用することが推奨されます。

## 注意点・落とし穴

- **実行コストとリソースの残存リスク**: Terratest は実際にクラウドリソースを作成するため、テストが途中でクラッシュしたりタイムアウトした場合、`defer` が実行されずリソースが残ってしまうことがあります。CI では定期的に「タグ付けされたテスト用リソースを一括削除するクリーンアップジョブ」を用意しておくと安全です。
- **並列実行時の名前衝突**: `random.UniqueId()` や `random.UniqueDomainName()` などを使ってリソース名を一意にしないと、同時実行されるテスト同士が衝突します。
- **実行時間**: 実インフラをデプロイするため、単体テストのように秒単位では終わりません。VPC や EKS クラスタのテストは数分〜数十分かかることも珍しくなく、CI のタイムアウト設定を適切に調整する必要があります。
- **秘密情報の扱い**: テストコード内にクレデンシャルをハードコードせず、環境変数や IAM ロール、シークレットマネージャー経由で注入することが必須です。
- **リトライとエラーハンドリング**: クラウド API は一時的なレート制限やタイミングの問題で失敗することがあるため、`retry.DoWithRetry` などのヘルパーを使って一時的なエラーを吸収する設計が推奨されます。

## FAQ

**Q1. Terratest と `terraform plan` によるチェックの違いは何ですか?**
A. `terraform plan` は構成ファイルから「何が変更されるか」を静的に計算するものであり、実際にクラウド上でリソースが正しく動作するかまでは検証しません。Terratest は実際にリソースをデプロイし、HTTP アクセスや SDK 呼び出しを通じて実行時の振る舞いまで検証する点が大きく異なります。テストピラミッドで言えば、`plan` の検証は静的解析やユニットテストに近く、Terratest はインテグレーションテストに相当します。

**Q2. テストのたびに課金が発生しますが、コストを抑える方法はありますか?**
A. いくつかの工夫があります。まず、可能な限り小さいインスタンスタイプやマネージドサービスの最小構成を使うこと。次に、`test_structure` を使ってステージを分割し、デプロイと検証を切り離してデバッグ時の再デプロイ回数を減らすこと。さらに、CI 上ではプルリクエストごとに毎回フルスタックをデプロイするのではなく、変更のあったモジュールだけを対象にテストを絞り込む戦略も有効です。夜間バッチでのみエンドツーエンドテストを実行するといった頻度の調整も一般的です。

**Q3. state ファイルの管理で気をつけるべきことは何ですか?**
A. テスト用の state を本番の state と混在させないことが最も重要です。Terratest 実行時はテスト専用のバックエンド設定や一時ディレクトリを使い、本番の state ファイルには一切触れないようにします。また、CI で並列実行する場合はテストごとに一意な state キーやワークスペースを割り当て、ロック競合やリソースの二重管理を防ぐ必要があります。テスト終了後は `defer terraform.Destroy` を確実に呼び出し、リソースと state の双方をクリーンな状態に戻すことを徹底してください。

## まとめ

Terratest は Terraform コードに対して「実際にデプロイして検証する」という、静的解析だけでは得られない安心感を提供してくれるツールです。モジュール単位でのテスト設計、state の分離、リソースの確実なクリーンアップという基本方針を守ることで、AWS・GCP・Azure いずれの環境でも安全かつ継続的にインフラコードの品質を担保できます。まずは小さなモジュール単位のテストから導入し、CI パイプラインに組み込みながら、段階的にエンドツーエンドテストへと拡張していくアプローチをおすすめします。
