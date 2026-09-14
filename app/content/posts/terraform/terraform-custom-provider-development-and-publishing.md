---
title: 'Terraformカスタムプロバイダー開発と公開の実践ガイド'
date: 2026-09-14
category: terraform
slug: terraform-custom-provider-development-and-publishing
summary: 'Terraformは標準でAWS、GCP、Azureなど主要クラウドベンダーのプロバイダーを提供していますが、社内の独自API、SaaS製品、あるいはニッチなインフラを管理したい場合、既存プロバイダーではカバーできないことがあります。そうしたケースで力を発揮するのが「カスタムプロバイダー」です。本記事では、Ter…'
lang: ja
---

# Terraformカスタムプロバイダー開発と公開の実践ガイド

Terraformは標準でAWS、GCP、Azureなど主要クラウドベンダーのプロバイダーを提供していますが、社内の独自API、SaaS製品、あるいはニッチなインフラを管理したい場合、既存プロバイダーではカバーできないことがあります。そうしたケースで力を発揮するのが「カスタムプロバイダー」です。本記事では、Terraformプロバイダーの基本概念から実装、state管理、モジュール化、公開までを一通り解説します。

## 1. Terraformプロバイダーとは何か

Terraformにおけるプロバイダーは、Terraformコアと外部システム(API)の橋渡しをするプラグインです。Terraformコア自体はHCLの解析、依存関係グラフの構築、実行計画(plan)の作成といった汎用的な処理を担い、実際に「リソースを作成する」「更新する」「削除する」という具体的な処理はすべてプロバイダーに委譲されます。

プロバイダーは内部的に以下の要素で構成されます。

- **Provider**: 認証情報や共通設定(APIエンドポイント、リージョンなど)を保持するトップレベルの定義
- **Resource**: `terraform apply`で作成・変更・削除されるオブジェクトの単位(例: `aws_instance`)
- **Data Source**: 既存のオブジェクトを参照のみ行う仕組み(例: `data "aws_ami"`)
- **Schema**: 各リソース・データソースが受け取る引数と出力する属性の型定義

Terraformプロバイダーは現在、HashiCorpが提供する**Terraform Plugin Framework**(旧SDKv2からの移行先)を使ってGo言語で実装するのが標準的な方法です。gRPCを介してTerraformコアと通信するため、言語自体はGoである必要がありますが、内部で任意のREST API、gRPC API、CLIラッパーなどを呼び出すことができます。

## 2. 開発環境のセットアップ

Terraform Plugin Frameworkを使ったプロバイダー開発の基本構成は次のようになります。

```
terraform-provider-example/
├── main.go
├── go.mod
├── internal/
│   ├── provider/
│   │   ├── provider.go
│   │   ├── resource_widget.go
│   │   └── data_source_widget.go
└── examples/
    └── resources/
        └── example_widget/
            └── resource.tf
```

`main.go`ではプロバイダーサーバーを起動します。

```go
package main

import (
    "context"
    "log"

    "github.com/hashicorp/terraform-plugin-framework/providerserver"
    "github.com/yourorg/terraform-provider-example/internal/provider"
)

func main() {
    err := providerserver.Serve(context.Background(), provider.New, providerserver.ServeOpts{
        Address: "registry.terraform.io/yourorg/example",
    })
    if err != nil {
        log.Fatal(err)
    }
}
```

`Address`にはTerraform Registryへの公開を見据えたアドレス形式(`ホスト名/組織名/プロバイダー名`)を指定します。ローカル開発中は`~/.terraformrc`に`dev_overrides`を設定することで、ビルドしたバイナリを直接参照して動作確認できます。

```hcl
provider_installation {
  dev_overrides {
    "registry.terraform.io/yourorg/example" = "/Users/you/go/bin"
  }
  direct {}
}
```

## 3. リソースの実装とHCL例

リソースは`Schema`、`Create`、`Read`、`Update`、`Delete`の各メソッドを持つ構造体として実装します。

```go
type WidgetResource struct {
    client *ExampleClient
}

func (r *WidgetResource) Schema(ctx context.Context, req resource.SchemaRequest, resp *resource.SchemaResponse) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
            "id": schema.StringAttribute{
                Computed: true,
            },
            "name": schema.StringAttribute{
                Required: true,
            },
            "size": schema.Int64Attribute{
                Optional: true,
            },
        },
    }
}

func (r *WidgetResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
    var plan WidgetModel
    req.Plan.Get(ctx, &plan)

    widget, err := r.client.CreateWidget(plan.Name.ValueString(), plan.Size.ValueInt64())
    if err != nil {
        resp.Diagnostics.AddError("Widgetの作成に失敗しました", err.Error())
        return
    }

    plan.ID = types.StringValue(widget.ID)
    resp.State.Set(ctx, &plan)
}
```

このリソースをユーザーが利用する場合、HCLは次のように書きます。

```hcl
terraform {
  required_providers {
    example = {
      source  = "yourorg/example"
      version = "~> 1.0"
    }
  }
}

provider "example" {
  api_endpoint = "https://api.example.com"
  api_token    = var.example_api_token
}

resource "example_widget" "main" {
  name = "production-widget"
  size = 10
}

output "widget_id" {
  value = example_widget.main.id
}
```

`Read`メソッドは、実際のインフラの状態を都度APIから取得してstateと同期させる役割を持ちます。これがドリフト検出(`terraform plan`で差分が出る仕組み)の根幹です。`Update`では変更可能な属性のみをAPIに反映し、変更できない属性(例えば名前の変更にリソース再作成が必要な場合)は`RequiresReplace`をスキーマに指定します。

## 4. State管理との関係

カスタムプロバイダーであっても、stateの扱いはTerraformコアが一元管理するため、プロバイダー開発者はstateファイルのフォーマットを直接意識する必要はありません。プロバイダーが返す属性値がそのままstateに書き込まれます。ただし、以下の点は設計上重要です。

- **機密情報の扱い**: APIキーやパスワードなど機密性の高い属性は`Sensitive: true`を指定してもstateファイル自体は平文で保存されるため、リモートバックエンド(S3+DynamoDB、Terraform Cloudなど)での暗号化・アクセス制御が前提になります。
- **Import機能**: 既存リソースをTerraform管理下に置くための`ImportState`を実装しておくと、運用開始時の移行が容易になります。
- **状態の一意性**: `id`属性はリソースを一意に識別できる値である必要があり、Read/Update/Deleteはこの`id`を起点にAPIを呼び出します。

```hcl
# 既存リソースをimportする例
terraform import example_widget.main widget-12345
```

## 5. モジュール化のベストプラクティス

カスタムプロバイダーを使う側の利用者にとっては、モジュールで抽象化することで再利用性が高まります。

```hcl
# modules/widget/main.tf
variable "name" {
  type = string
}

variable "size" {
  type    = number
  default = 5
}

resource "example_widget" "this" {
  name = var.name
  size = var.size
}

output "id" {
  value = example_widget.this.id
}
```

```hcl
# ルートモジュールでの利用
module "widget_dev" {
  source = "./modules/widget"
  name   = "dev-widget"
  size   = 1
}
```

プロバイダー開発側でも、公式ドキュメント生成のために`terraform-plugin-docs`を使い、`examples/`ディレクトリのHCLからREADMEやRegistry掲載用ドキュメントを自動生成できるようにしておくと、モジュール利用者が迷わずに済みます。

## 6. Terraform Registryへの公開

自作プロバイダーはGitHub Releases経由でTerraform Public Registryに公開できます。手順の要点は以下の通りです。

1. GPGキーでリリースバイナリに署名する
2. [GoReleaser](https://goreleaser.com/)を使い、複数OS/アーキテクチャ向けにクロスビルドする
3. GitHub Actionsでタグpush時に自動リリースするワークフローを組む
4. Terraform Registryにリポジトリを連携し、GPG公開鍵を登録する

```yaml
# .goreleaser.yml (抜粋)
builds:
  - env: [CGO_ENABLED=0]
    goos: [darwin, linux, windows]
    goarch: [amd64, arm64]
signs:
  - artifacts: checksum
    args: ["--batch", "-u", "{{ .Env.GPG_FINGERPRINT }}", "--output", "${signature}", "--detach-sign", "${artifact}"]
```

社内専用で公開登録が不要な場合は、Private Registry(Terraform Cloud/EnterpriseのPrivate Registry機能)やローカルファイルシステムミラー(`filesystem_mirror`)を使う方法もあります。

## 7. 注意点

- **バージョニング**: スキーマ変更は破壊的変更になりやすいため、セマンティックバージョニングを厳格に守り、`required_providers`のバージョン制約を利用者に明示することが重要です。
- **並行実行とレート制限**: Terraformはリソースをグラフの依存関係に基づき並列実行します。バックエンドAPIにレート制限がある場合、プロバイダー内でリトライやバックオフを実装しないと`apply`が頻繁に失敗します。
- **エラーメッセージの質**: `Diagnostics.AddError`で返すメッセージは利用者が直接目にするため、原因と対処法が分かる文言にする必要があります。
- **SDKv2からの移行**: 既存プロバイダーの多くはまだSDKv2ベースですが、HashiCorpはPlugin Frameworkへの移行を推奨しており、新規開発ではFrameworkを選ぶのが無難です。
- **テスト**: `terraform-plugin-testing`を用いたacceptance testでは、実際にAPIへリクエストを送るため、CI環境でのテスト用APIキー管理やコスト管理も考慮が必要です。

## 8. AWS/GCP/Azureとの関係

AWS・GCP・Azureの公式プロバイダー(`hashicorp/aws`、`hashicorp/google`、`hashicorp/azurerm`)も、本記事で紹介した仕組みと基本的に同じ構造(Plugin Framework or SDKv2)で実装されています。したがって、これらの公式プロバイダーのソースコードはカスタムプロバイダー開発時の優れた参考実装になります。特に、大量のリソースタイプを扱う際のコード生成手法(AWSプロバイダーのコードジェネレーターなど)は、独自プロバイダーが成長した際のメンテナンス性向上に役立ちます。また、自社インフラがAWS/GCP/Azure上に構築されている場合、カスタムプロバイダーの中から公式プロバイダーのGo SDK(AWS SDK for Go、google-cloud-go、Azure SDK for Goなど)を呼び出して、複数クラウドの操作を一つの独自リソースにラップするという設計も可能です。例えば「AWSのS3バケット作成+社内SaaSへの登録」を1つの`resource`にまとめるといった使い方が考えられます。

## FAQ

**Q1. カスタムプロバイダーは有償のTerraform Cloud/Enterpriseがないと使えませんか?**
A. いいえ、OSS版のTerraform CLIだけで開発・利用が可能です。Private Registry機能を使わない場合でも、`dev_overrides`やファイルシステムミラーでチーム内配布ができます。有償版が必要になるのは、Sentinelポリシーやプライベートレジストリの高度な権限管理を使いたい場合です。

**Q2. Go以外の言語でプロバイダーを書けますか?**
A. Terraformコアとの通信はgRPCベースのプロトコルで行われるため理論上は他言語での実装も不可能ではありませんが、公式SDK(Plugin Framework/SDKv2)はGo向けにしか提供されておらず、実用上はGoが事実上の必須言語です。内部ロジックから他言語で書かれた既存ツールをCLI経由やHTTP経由で呼び出すことは問題ありません。

**Q3. プロバイダーとモジュールの違いが分かりません。どちらを作るべきですか?**
A. プロバイダーはTerraformとAPIをつなぐ「低レベルの部品」であり、モジュールはそのプロバイダーが提供するリソースを組み合わせて再利用可能にする「高レベルの部品」です。既存の公式プロバイダー(AWS/GCP/Azureなど)で対象システムを操作できるなら、まずモジュールで抽象化を検討し、そもそも対象システムに対応するプロバイダーが存在しない場合にのみカスタムプロバイダーの開発を検討するのが妥当です。
