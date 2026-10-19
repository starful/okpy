---
title: 'Terraform デバッグ実践ガイド：ログと依存関係グラフで問題を可視化する'
date: 2026-10-12
category: terraform
slug: terraform-debugging-with-logs-and-resource-graph-visualization
summary: 'Terraform でインフラを構築していると、`apply` が途中で失敗したり、意図しないリソースが作成・削除されたりするトラブルに必ず遭遇します。こうした問題を効率的に解決するためには、Terraform が提供するログ機能とリソースグラフの可視化機能を正しく使いこなすことが重要です。本記事では、Terra…'
lang: ja
---

# Terraform デバッグ実践ガイド：ログと依存関係グラフで問題を可視化する

Terraform でインフラを構築していると、`apply` が途中で失敗したり、意図しないリソースが作成・削除されたりするトラブルに必ず遭遇します。こうした問題を効率的に解決するためには、Terraform が提供するログ機能とリソースグラフの可視化機能を正しく使いこなすことが重要です。本記事では、Terraform のデバッグに使える主要な仕組みを、概念・HCL例・state の扱い・モジュール設計・注意点・FAQ の順に実践的に解説します。

## 1. Terraform デバッグの基本概念

Terraform は内部的に以下のステップで動作しています。

1. HCL（HashiCorp Configuration Language）の構文解析
2. リソース間の依存関係からの実行計画（DAG：有向非巡回グラフ）の構築
3. プロバイダー経由での API 呼び出し（CRUD操作）
4. state ファイルへの結果の反映

デバッグが必要になるのは、主にこの4つのどこかで想定外の挙動が起きたときです。たとえば「なぜこのリソースが先に作成されたのか」「なぜ値が期待通りに解決されないのか」「なぜ apply が特定のリソースでハングするのか」といった疑問は、それぞれログ出力とグラフ可視化で原因を特定できます。

### 1.1 ログレベルと `TF_LOG`

Terraform はログレベルを環境変数 `TF_LOG` で制御します。

```bash
export TF_LOG=TRACE
export TF_LOG_PATH="./terraform-debug.log"
terraform apply
```

主なログレベルは以下の通りです。

| レベル | 用途 |
|---|---|
| `TRACE` | 最も詳細。プロバイダーとのAPI通信内容まで出力 |
| `DEBUG` | 内部処理のステップを出力 |
| `INFO` | 通常の進行状況 |
| `WARN` | 警告のみ |
| `ERROR` | エラーのみ |

プロバイダー個別のログを分けたい場合は `TF_LOG_PROVIDER` や `TF_LOG_CORE` を使うことで、Terraform 本体とプロバイダープラグインのログを分離できます。大規模な構成では全体を `TRACE` にすると出力量が膨大になるため、まず `DEBUG` で問題範囲を絞り、必要な箇所だけ `TRACE` に上げるのが実践的です。

```bash
export TF_LOG_CORE=DEBUG
export TF_LOG_PROVIDER=TRACE
```

## 2. HCL 例で見るデバッグポイント

### 2.1 依存関係が不明瞭なケース

暗黙の依存関係（implicit dependency）はリソース参照から自動的に推測されますが、参照が存在しない場合は `depends_on` で明示する必要があります。

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "okpy-app-logs"
}

resource "aws_iam_role_policy" "allow_logging" {
  name   = "allow-s3-logging"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.logging.json

  depends_on = [aws_s3_bucket.logs]
}
```

このような明示的依存は、グラフ上では通常の参照エッジと同様に表示されますが、`terraform graph` の出力を見ないと見落としやすいポイントです。

### 2.2 `for_each` によるリソース展開のデバッグ

`for_each` を使った動的なリソース生成では、キーの不整合がエラーの原因になりやすいです。

```hcl
variable "environments" {
  type    = set(string)
  default = ["dev", "staging", "prod"]
}

resource "aws_vpc" "main" {
  for_each   = var.environments
  cidr_block = "10.${index(tolist(var.environments), each.key)}.0.0/16"

  tags = {
    Name = "vpc-${each.key}"
  }
}
```

`terraform plan` の差分が意図と異なる場合は、まず `terraform console` でその場で式を評価して確認するのが有効です。

```bash
terraform console
> var.environments
> index(tolist(var.environments), "staging")
```

## 3. リソースグラフの可視化

Terraform には、構成全体の依存関係を DOT 形式で出力する `terraform graph` コマンドがあります。これを Graphviz などでレンダリングすることで、リソース間の依存関係を視覚的に把握できます。

```bash
terraform graph > graph.dot
dot -Tsvg graph.dot -o graph.svg
```

plan フェーズのグラフだけでなく、apply フェーズのグラフも別途出力できます。

```bash
terraform graph -type=plan > plan-graph.dot
terraform graph -type=apply > apply-graph.dot
```

大規模な構成ではノード数が多すぎて可読性が落ちるため、特定モジュールだけを対象に絞り込みたい場合は `-module-depth` オプションや、`grep` でDOTファイルをフィルタしてから描画する方法が実用的です。

```bash
grep -E "module.network" graph.dot > network-graph.dot
```

グラフを見ることで、以下のような問題が発見できます。

- 想定していないリソース間の暗黙依存（循環参照の予兆）
- モジュール境界をまたぐ過剰な結合
- 並列実行されるはずのリソースが直列化されている原因

循環依存が発生すると `Error: Cycle: ...` というエラーが出ますが、エラーメッセージだけでは全体像が掴みにくいため、グラフを描いて該当ノード周辺を確認するのが最も早い解決方法です。

## 4. state のデバッグ

### 4.1 state の中身を調べる

`terraform state` サブコマンド群は、実際にどのリソースが state に記録されているかを確認する基本手段です。

```bash
terraform state list
terraform state show aws_vpc.main["staging"]
```

plan の差分が「リソースが存在するのに新規作成扱いになる」といった場合、state に該当リソースが記録されていない可能性が高く、`terraform state list` で真っ先に確認すべきです。

### 4.2 import と state の不整合解消

手動で作成されたリソースや、他のツールで管理されているリソースを取り込む場合は `import` ブロックまたは `terraform import` コマンドを使います。

```hcl
import {
  to = aws_instance.bastion
  id = "i-0123456789abcdef0"
}

resource "aws_instance" "bastion" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.micro"
}
```

import 後に `terraform plan` で差分がゼロにならない場合、HCL の設定値が実際のリソース属性と一致していないことを示します。この差分自体が、実インフラと設定のズレを発見するための重要なデバッグ情報になります。

### 4.3 state ロックとリモートバックエンド

チームで作業する場合、state の競合はよくあるトラブルです。S3 + DynamoDB のようなリモートバックエンドを使っていれば、ロック情報を確認できます。

```bash
terraform force-unlock <LOCK_ID>
```

`force-unlock` は強制操作のため、本当に他の `apply` が実行中でないことを確認してから使う必要があります。

## 5. モジュールのデバッグ

モジュールを多用する構成では、問題がどのモジュール内で起きているかを特定することが最初のステップになります。

```hcl
module "network" {
  source = "./modules/network"

  vpc_cidr = "10.0.0.0/16"
}

module "app" {
  source = "./modules/app"

  vpc_id  = module.network.vpc_id
  subnets = module.network.private_subnet_ids
}
```

モジュール単体でのデバッグには `-target` オプションが有効です。

```bash
terraform plan -target=module.network
terraform apply -target=module.network
```

ただし `-target` は本来一時的な調査・復旧用の機能であり、常用すると依存関係の整合性が崩れるリスクがあります。恒常的にモジュール単位で分けて適用したい場合は、Terraform Workspace やルートモジュールの分割を検討すべきです。

モジュール内部で出力されるログを明確にしたい場合、`output` ブロックに `description` を付けておくと、`terraform output` やグラフ上でも意味が追いやすくなります。

```hcl
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "Network module が作成した VPC の ID"
}
```

## 6. クラウドプロバイダーごとの関連ポイント

- **AWS**: `TF_LOG_PROVIDER=TRACE` にすると、AWS SDK が発行する実際の API リクエスト（`CreateVpc` や `RunInstances` など）が確認でき、IAM権限不足やスロットリングの原因特定に役立ちます。CloudTrail と組み合わせて突き合わせるとさらに精度が上がります。
- **GCP**: Google プロバイダーは API 有効化忘れ（`googleapi: Error 403`）がエラーの大半を占めます。TRACE ログで実際に呼ばれている Google Cloud API エンドポイントを確認し、Cloud Console の「APIとサービス」で有効化状況を照合します。
- **Azure**: AzureRM プロバイダーは ARM テンプレートへの変換処理を内部で行うため、エラーメッセージが抽象的になりがちです。TRACE ログで実際の ARM リクエストボディを確認すると、どのプロパティが拒否されているかが明確になります。

いずれのクラウドでも共通するのは、「Terraform自体のロジックの問題」と「プロバイダーAPI側の問題」を切り分けるために、`TF_LOG_CORE` と `TF_LOG_PROVIDER` を分けて確認する習慣が有効だという点です。

## 7. 実践上の注意点

- **ログファイルに機密情報が出力される**：TRACE レベルでは認証情報やリクエストボディがそのままログに残ることがあります。ログファイルを共有・保存する際はマスキングや破棄のルールを決めておきましょう。
- **グラフは「計画」の静的な表現**：`terraform graph` は現在の設定から計算される依存関係を表示するものであり、実行中の動的なエラー（タイムアウトやAPI制限）はグラフには現れません。ログと併用することが前提です。
- **`-target` の多用は技術的負債になる**：一時的なデバッグ手段として便利ですが、CI/CDパイプラインに組み込むと依存関係の不整合を隠蔽したまま運用され続けるリスクがあります。
- **state 操作は必ずバックアップを取る**：`state rm`、`state mv`、`force-unlock` などの操作を行う前に、リモートバックエンドのバージョニングや `terraform state pull > backup.tfstate` でのバックアップを必ず取得してください。

## FAQ

**Q1. `TF_LOG=TRACE` にしてもログが出力されない場合は？**

`TF_LOG_PATH` を設定していない場合、ログは標準エラー出力にしか出ません。ターミナルの出力をリダイレクトしていないか、あるいは別のシェルセッションで環境変数が引き継がれていないかを確認してください。また、Terraform Cloud/Enterprise 上で実行している場合は、ログの取得方法がローカル実行と異なり、実行ログのUIから確認する必要があります。

**Q2. `terraform graph` の出力が複雑すぎて読めないときはどうすればよいですか？**

ノード数が多い場合は、まず問題の起きているリソースタイプやモジュール名で `grep` して部分グラフを抽出するのが実用的です。加えて、Graphviz の `-Gsplines=true` や `-Granksep` オプションでレイアウトを調整すると可読性が上がります。恒常的に複雑すぎる場合は、モジュール分割自体を見直すサインでもあります。

**Q3. state に記録されているリソースと実際のクラウド上のリソースが一致しないのはなぜですか？**

多くの場合、手動変更（コンソールからの直接編集）や他のIaCツールとの併用が原因です。`terraform plan -refresh-only` を実行すると、実際のインフラ状態と state の差分だけを確認でき、意図しない drift（ドリフト）を把握できます。恒常的なdrift検知が必要な場合は、CI上で定期的に `plan -refresh-only` を走らせる運用がおすすめです。

---

Terraform のデバッグは、ログで「何が実行されたか」を追い、グラフで「なぜその順序・依存関係になったか」を理解し、state で「現在何が記録されているか」を確認するという3つの視点を組み合わせることで、ほとんどの問題を体系的に解決できます。特に大規模なモジュール構成やマルチクラウド環境では、この3点をセットで確認する習慣が、トラブルシューティングの時間を大きく短縮します。
