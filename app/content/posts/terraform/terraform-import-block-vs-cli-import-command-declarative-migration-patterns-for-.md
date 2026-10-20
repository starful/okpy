---
title: 'Terraform import block vs CLI import コマンド:既存インフラを宣言的に移行するパターン'
date: 2026-10-20
category: terraform
slug: terraform-import-block-vs-cli-import-command-declarative-migration-patterns-for-
summary: 'Terraform でクラウド上に手動構築された既存リソースを管理対象に加える作業は、長らく `terraform import` という CLI コマンドに依存していました。しかし Terraform 1.5 以降で導入された `import` ブロックにより、インポート作業自体を HCL コードとして宣言でき…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261020185123.jpg'
lang: ja
---

# Terraform import block vs CLI import コマンド:既存インフラを宣言的に移行するパターン

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261020185123.jpg)


## はじめに

Terraform でクラウド上に手動構築された既存リソースを管理対象に加える作業は、長らく `terraform import` という CLI コマンドに依存していました。しかし Terraform 1.5 以降で導入された `import` ブロックにより、インポート作業自体を HCL コードとして宣言できるようになりました。本記事では両者の違いを整理し、既存インフラをどのように安全に Terraform 管理下へ移行するかを、HCL の実例と state の扱い、モジュール構成、注意点を交えて解説します。

## `terraform import` CLI とは何か

`terraform import` は、すでにクラウド上に存在するリソース(例えば手動で作成した EC2 インスタンスや GCS バケット)を、Terraform の state ファイルに登録するためのコマンドです。

```bash
terraform import aws_instance.web i-0123456789abcdef0
```

このコマンドは「state にリソースを紐づける」ことしか行いません。対応する HCL コード(`resource "aws_instance" "web" { ... }`)は事前に自分で書いておく必要があります。コード側の属性と実際のリソースの属性が一致していなければ、次の `terraform plan` で差分が検出され、意図しない変更が適用されるリスクがあります。

CLI import の課題は以下の通りです。

- インポート操作がコードとして残らず、再実行性(再現性)がない
- 一度に 1 リソースずつしか処理できず、大量リソースの移行には不向き
- CI/CD パイプライン内で `terraform import` を実行するのは副作用が強く、レビューを経ずに state を変更してしまう

## `import` ブロックとは何か

Terraform 1.5 で導入された `import` ブロックは、インポート操作そのものを HCL で宣言し、`terraform plan` の中でプレビューできるようにした機能です。

```hcl
import {
  to = aws_instance.web
  id = "i-0123456789abcdef0"
}

resource "aws_instance" "web" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.micro"
  tags = {
    Name = "web-server"
  }
}
```

`terraform plan` を実行すると、Terraform は指定した ID のリソースを読み込み、`resource` ブロックとの差分を plan 出力に表示します。これにより、インポート前に「このリソースが適用後にどう変化するか」を確認でき、CLI import にはなかったレビュー可能性が得られます。

さらに Terraform 1.7 以降では `for_each` を使って複数リソースを一括インポートできます。

```hcl
locals {
  existing_buckets = {
    "logs"   = "my-company-logs-bucket"
    "assets" = "my-company-assets-bucket"
  }
}

import {
  for_each = local.existing_buckets
  to       = google_storage_bucket.buckets[each.key]
  id       = each.value
}

resource "google_storage_bucket" "buckets" {
  for_each = local.existing_buckets
  name     = each.value
  location = "ASIA-NORTHEAST1"
}
```

これにより数十〜数百リソースの移行をコードレビューを通した PR として扱えるようになります。

## `terraform plan -generate-config-out` との組み合わせ

既存リソースの HCL をゼロから手書きするのは現実的でない場合が多いため、`import` ブロックと `-generate-config-out` オプションを組み合わせるのが実践的なワークフローです。

```bash
terraform plan -generate-config-out=generated.tf
```

`import` ブロックのみを書いた状態でこのコマンドを実行すると、Terraform が実際のリソース属性から HCL を自動生成してくれます。生成されたコードは完璧ではないため、不要な computed 属性の削除や変数化などの手直しは必須ですが、ゼロから書くより圧倒的に効率的です。

典型的な移行フローは次のようになります。

1. 対象リソースの ID を調べる(クラウドコンソールや CLI)
2. `import` ブロックのみ記述する
3. `terraform plan -generate-config-out=generated.tf` を実行して HCL を生成
4. 生成コードをレビューし、変数化・tag 整理などを行う
5. `terraform plan` で差分がゼロ(または意図した差分のみ)であることを確認
6. `terraform apply` で state にリソースを取り込む
7. `import` ブロックを削除する(恒久的に残す必要はない)

## state への影響

CLI import も `import` ブロックも、最終的に行っていることは同じで、「実際のリソースと Terraform state のマッピングを作る」ことです。違いは実行タイミングと可視性にあります。

- CLI import:`terraform import` 実行時点で即座に state が書き換わる。plan のレビューを経ない。
- import ブロック:`terraform apply` 実行時に state が書き換わる。事前に `plan` で差分を確認できる。

どちらの方式でも、インポート後に `terraform plan` を実行して差分がないことを確認する作業は欠かせません。属性の不一致(例えば `lifecycle_rule` の順序や、デフォルト値が設定されていないケース)があると、次の apply で意図しない再作成やプロパティ変更が発生する可能性があります。特に `force_destroy` や `versioning` のような一部クラウド側のみで変更可能な属性は要注意です。

## モジュール内のリソースをインポートする

モジュール配下のリソースをインポートする場合、`to` にはモジュールパスを含めたアドレスを指定します。

```hcl
import {
  to = module.network.aws_subnet.private["ap-northeast-1a"]
  id = "subnet-0123456789abcdef0"
}
```

モジュールが `for_each` や `count` を使っている場合、インデックスキーまで正確に一致させる必要があります。ここを誤ると「別のリソースとしてインポートされてしまう」「state 上で重複が発生する」といった事故につながるため、`terraform state list` で既存のアドレス構造を確認しながら作業するのが安全です。

もう一つの選択肢として、`moved` ブロックとの併用があります。インポート後にモジュール構成を変更する予定がある場合、`import` と `moved` を同じ PR に含めることで、インポートとリファクタリングを一度に宣言的に表現できます。

```hcl
moved {
  from = aws_subnet.private
  to   = module.network.aws_subnet.private["ap-northeast-1a"]
}
```

## AWS / GCP / Azure との関係

インポート機能自体はクラウド中立な Terameta Core 機能ですが、実際に重要になるのは各プロバイダーの「インポート可能な ID 形式」です。

- **AWS**:多くのリソースはリソース ID(`i-xxxx`、ARN など)でインポートします。IAM ポリシーのアタッチメントのように複合キー(`user_name/policy_arn` のような文字列結合)を要求するリソースもあり、プロバイダーのドキュメントで import 用 ID フォーマットを必ず確認する必要があります。
- **GCP**:プロジェクト ID やリージョンを含む完全パス形式(`projects/{project}/locations/{location}/...`)が多く、`google` プロバイダーのバージョンによって要求される ID 形式が変わることがあります。
- **Azure**:Azure Resource Manager の完全なリソース ID(`/subscriptions/.../resourceGroups/.../providers/...`)をそのまま `id` に指定するケースが大半です。長大な文字列になるため、`data.azurerm_resources` などで動的に取得して `for_each` に渡す構成が実践的です。

複数クラウドを横断するプラットフォームチームでは、インポート用の ID をどう収集するか(各クラウドの CLI、ポリシー as コードツール、タグ検索など)を事前に決めておくと、`import` ブロックの `for_each` 構築が楽になります。

## 注意点・落とし穴

- **state ロックとバックエンド**:リモートバックエンド(S3+DynamoDB、GCS、Azure Storage など)を使っている場合、インポート作業中も通常の apply と同様に state ロックがかかります。CI 上で並行実行しているパイプラインと衝突しないよう注意してください。
- **シークレット・センシティブ値**:インポートされたリソースにシークレット値(DB パスワードなど)が含まれる場合、`generate-config-out` で生成されたコードに平文で出力されることがあります。生成後は必ず `sensitive = true` の付与や変数化を行ってください。
- **ドリフトの蓄積**:インポート前に手動変更が積み重なっているリソースほど、plan 時の差分が大きくなります。インポート前に一度リソースの現状を棚卸しし、不要な属性を削除しておくと移行がスムーズです。
- **import ブロックは一回限り**:apply 完了後も `import` ブロックをコードに残しておくと、次回の plan でも再度インポート処理が走り警告が出ることがあります。移行が完了したら削除するのを忘れないでください。
- **バージョン要件**:`import` ブロックの複数リソース一括処理(`for_each`)は Terraform 1.7 以降が必要です。古い Terraform バージョンを使っている CI 環境では CLI import に頼らざるを得ない場合があります。

## FAQ

**Q1. 既存の `terraform import` コマンドはもう使えなくなるのですか?**
A. いいえ、`terraform import` CLI コマンドは非推奨ではなく、現在も利用可能です。単発のリソースをインタラクティブに取り込みたい場合や、古い Terraform バージョンを使っている環境では依然として有効な手段です。ただし、チームでのレビュー・再現性を重視する場合は `import` ブロックへの移行が推奨されます。

**Q2. `import` ブロックを使えば HCL を手書きしなくて済みますか?**
A. `terraform plan -generate-config-out` を併用すれば自動生成は可能ですが、生成されたコードはそのまま本番運用に適した品質とは限りません。デフォルト値の明示、変数化、不要な computed 属性の削除など、人間によるレビューと手直しは必須です。

**Q3. モジュールをまたいでリソースを移動しつつインポートすることはできますか?**
A. 可能です。インポート対象が既にどこかの state にある場合は `moved` ブロック、まだ Terraform 管理外の場合は `import` ブロックを使います。両者を同じ PR 内で併用し、モジュール構成のリファクタリングとインポートを一度に宣言的に表現するのが一般的なパターンです。

## まとめ

`terraform import` CLI は手軽で即時的ですが、コードとして残らずレビューを経ないという弱点があります。一方 `import` ブロックは HCL として宣言できるため、`plan` によるレビュー、`for_each` による一括処理、`generate-config-out` によるコード自動生成といった恩恵を受けられます。既存インフラの移行を安全かつチームで検証可能な形で進めたいのであれば、今後は `import` ブロックを第一候補とし、CLI import は単発作業や古いバージョン環境向けの補助手段として位置づけるのが実践的です。
