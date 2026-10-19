---
title: 'Terraform Plan Output Explained: 差分の読み方、JSON Plan のエクスポート、CI レビュー自動化'
date: 2026-10-19
category: terraform
slug: terraform-plan-output-explained-reading-diffs-json-plan-export-and-ci-review-aut
summary: 'Terraform を使ったインフラ管理において、`terraform plan` の出力を正確に読み解く能力は、安全なデプロイの土台となります。特にチーム開発やCI/CDパイプラインにPlanを組み込む場合、人間が目視で確認するだけでなく、構造化されたデータとして扱い自動レビューに組み込むことが重要になります。…'
lang: ja
---

# Terraform Plan Output Explained: 差分の読み方、JSON Plan のエクスポート、CI レビュー自動化

## はじめに

Terraform を使ったインフラ管理において、`terraform plan` の出力を正確に読み解く能力は、安全なデプロイの土台となります。特にチーム開発やCI/CDパイプラインにPlanを組み込む場合、人間が目視で確認するだけでなく、構造化されたデータとして扱い自動レビューに組み込むことが重要になります。本稿では、Plan出力の基本的な読み方から、JSON形式でのエクスポート、そしてCIでの差分レビュー自動化までを実践的に解説します。

## Terraform Plan の基本概念

`terraform plan` は、現在の State（状態ファイル）と、HCLで記述された希望する構成（Desired State）を比較し、その差分を計算するコマンドです。実際にリソースを変更するわけではなく、「何が起こるか」をシミュレーションします。

Plan出力には主に以下の記号が使われます。

- `+` 作成されるリソース
- `-` 削除されるリソース
- `~` 更新されるリソース(in-place update)
- `-/+` 削除後に再作成されるリソース(replace)
- `<=` データソースの読み込み

これらの記号を正しく読めることが、意図しない削除や再作成(特に`-/+`)を事前に検知する第一歩です。再作成は多くの場合、ダウンタイムやデータ損失のリスクを伴うため、Plan出力で最も注意深く見るべきポイントです。

## HCL の変更とPlan出力の対応例

以下は、AWSのEC2インスタンスのインスタンスタイプを変更する例です。

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.medium" # t3.small から変更
  tags = {
    Name = "web-server"
  }
}
```

このときのPlan出力は以下のようになります。

```
  # aws_instance.web will be updated in-place
  ~ resource "aws_instance" "web" {
        id            = "i-0123456789abcdef0"
      ~ instance_type = "t3.small" -> "t3.medium"
        tags          = {
            "Name" = "web-server"
        }
        # (28 unchanged attributes hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.
```

一方、AMIのIDを変更すると、多くのケースで`force-new`属性に該当し、以下のように再作成(replace)が発生します。

```
  # aws_instance.web must be replaced
-/+ resource "aws_instance" "web" {
      ~ ami           = "ami-0abcdef1234567890" -> "ami-0fedcba9876543210" # forces replacement
      ~ id            = "i-0123456789abcdef0" -> (known after apply)
        instance_type = "t3.medium"
    }

Plan: 1 to add, 0 to change, 1 to destroy.
```

`# forces replacement` というコメントが付いている属性こそが、再作成の直接的な原因です。この箇所を見落とすと、本番環境で予期しないリソースの作り直しが発生してしまいます。

## State との関係

Plan出力は、Stateファイル(`terraform.tfstate`)に記録されている現在のリソース情報と、コード上の定義を比較して生成されます。つまり、Stateが実際のクラウド上のリソースと一致していない(ドリフトしている)場合、Planの結果も不正確になります。

ドリフトを検知するには、通常のPlanに加えて `-refresh-only` オプションが有効です。

```bash
terraform plan -refresh-only
```

これにより、コード側の変更意図とは関係なく、「実際のリソースがStateと比べてどう変わったか」だけを確認できます。コンソールから手動でタグを変更した、といったケースの検知に有用です。

また、リソースをStateから除外・取り込みする`terraform state rm`や`terraform import`(または`import`ブロック)を使った後は、必ずPlanを実行して差分がゼロであることを確認する習慣をつけるとよいでしょう。

## モジュールとPlan出力の読み方

モジュールを利用している場合、Plan出力のリソースアドレスはモジュールパスを含む形式になります。

```hcl
module "network" {
  source = "./modules/network"
  cidr_block = "10.0.0.0/16"
}
```

```
  # module.network.aws_vpc.main will be updated in-place
  ~ resource "aws_vpc" "main" {
      ~ cidr_block = "10.1.0.0/16" -> "10.0.0.0/16"
    }
```

モジュールが入れ子になっている場合、アドレスは `module.parent.module.child.resource_type.name` のように連なっていきます。大規模な構成ではこのアドレスが非常に長くなるため、`-target` オプションで特定のリソースのみを対象にPlanを実行し、影響範囲を絞って確認する手法も実務では頻繁に使われます。

```bash
terraform plan -target="module.network.aws_vpc.main"
```

ただし`-target`は依存関係の整合性を崩すリスクがあるため、あくまで調査・デバッグ目的での利用に限定し、最終的な適用は全体Planで行うべきです。

## JSON Plan のエクスポートと活用

Plan出力をCIで自動処理する場合、人間向けのテキスト出力ではなく、機械判読可能なJSON形式を使うのが基本です。

```bash
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > plan.json
```

`plan.json` には `resource_changes` という配列があり、各要素に `address`、`change.actions`(例: `["update"]`、`["create"]`、`["delete", "create"]`など)、`change.before`/`change.after` が含まれます。`actions` に `delete` と `create` が両方含まれている場合、それはテキスト出力の `-/+` に相当する再作成を意味します。

`jq` を使えば、再作成されるリソースだけを素早く抽出できます。

```bash
jq -r '.resource_changes[]
  | select(.change.actions == ["delete", "create"])
  | .address' plan.json
```

同様に、削除のみが発生するリソースを検出する例です。

```bash
jq -r '.resource_changes[]
  | select(.change.actions == ["delete"])
  | .address' plan.json
```

本番環境向けのワークスペースでこのクエリの結果が空でない場合は、CIをfailさせてマージ前に人間のレビューを強制する、といった運用が可能になります。

## CI でのレビュー自動化の実装例

GitHub Actionsを例に、Plan結果をPRにコメントしつつ、危険な変更(削除や再作成)を検知する簡単なワークフローを示します。

```yaml
name: terraform-plan
on:
  pull_request:
    paths:
      - "infra/**"

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3

      - name: Terraform Init
        run: terraform init
        working-directory: infra

      - name: Terraform Plan
        run: terraform plan -out=tfplan.binary
        working-directory: infra

      - name: Export JSON
        run: terraform show -json tfplan.binary > plan.json
        working-directory: infra

      - name: Check for destructive changes
        working-directory: infra
        run: |
          DESTROY=$(jq '[.resource_changes[]
            | select(.change.actions | index("delete"))] | length' plan.json)
          if [ "$DESTROY" -gt 0 ]; then
            echo "::warning::削除を含む変更が ${DESTROY} 件検出されました。レビューを必ず行ってください。"
          fi

      - name: Post plan summary to PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const plan = JSON.parse(fs.readFileSync('infra/plan.json', 'utf8'));
            const summary = plan.resource_changes
              .map(r => `- \`${r.address}\`: ${r.change.actions.join(',')}`)
              .join('\n');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `### Terraform Plan Summary\n${summary}`
            });
```

このように、JSON Planをパースしてfailさせるかコメントするかを判断する処理を挟むことで、人間が全文を読まなくても危険な変更を見落としにくくなります。より高度な運用では、Open Policy Agent(OPA)の`conftest`やSentinelといったPolicy as Codeツールと組み合わせ、「特定タグがないリソースの削除は禁止」「本番環境でのセキュリティグループの0.0.0.0/0オープンは禁止」といったルールをコード化し、Plan JSONに対して自動検証することも一般的です。

```bash
conftest test --policy policy/ plan.json
```

## 注意点

- **`sensitive`な値のマスキング**: Plan出力やJSON出力には、`sensitive = true` と宣言した変数・属性の値が `(sensitive value)` として隠されますが、完全に安全というわけではありません。JSON出力をログやPRコメントに貼る際は、意図せず機密情報が含まれないか改めて確認してください。
- **`-/+` の見落とし**: 特にRDSやEC2のようなステートフルなリソースでの再作成は、データ消失やダウンタイムに直結します。`lifecycle { prevent_destroy = true }` を重要リソースに設定し、誤った再作成・削除をTerraform自体にブロックさせるのも有効な防御策です。
- **Plan結果と実際のApplyのズレ**: Planからの時間差やチームメンバーによる並行変更があると、Plan時点の内容とApply時点の内容がズレることがあります。CIでは `plan` と `apply` の間でStateロックを取得し、同一のPlanファイルを`apply tfplan.binary`のように指定して適用することで、このズレを防げます。
- **大規模リソースでの出力肥大化**: モジュールを多用する構成ではJSON出力が非常に大きくなることがあります。CIでの処理時間やアーティファクトサイズにも注意し、必要なら`-target`やワークスペース分割で管理範囲を分割することも検討してください。

## クラウドプロバイダーとの関係

Terraformはクラウド中立なツールであり、Plan出力の読み方自体はAWS・GCP・Azureのいずれでも共通です。ただし、プロバイダーごとに「何がforce-newになるか」の挙動は異なります。例えばAWSの`aws_instance`ではAMI変更が再作成を伴いますが、GCPの`google_compute_instance`ではブートディスクのイメージ変更の扱いが異なるケースがあり、Azureの`azurerm_linux_virtual_machine`でも同様に各属性ごとのforce-new仕様はプロバイダーのドキュメントで個別に確認する必要があります。マルチクラウド構成を取っている場合は、プロバイダーごとのPlan特性の違いを踏まえた上で、共通のCIレビューの仕組み(JSON抽出・Policy as Code)を適用するのが効率的です。

## FAQ

**Q1. `terraform plan` の結果は必ず `terraform apply` の結果と一致しますか?**

一致するとは限りません。Plan実行後にクラウド側で外部からの変更があった場合や、他のCI/CDパイプラインから並行してApplyが実行された場合、Plan時点の前提が崩れることがあります。確実性を高めるには、`terraform plan -out=tfplan.binary` で保存したバイナリファイルをそのまま `terraform apply tfplan.binary` で適用し、StateロックをCI全体で有効にする運用が推奨されます。

**Q2. JSON Plan出力はどのバージョンから利用できますか?**

`terraform show -json` はTerraform 0.12以降で利用可能です。ただし出力スキーマ自体はバージョンによって拡張されているため、CIで厳密なスキーマ検証を行う場合は、利用しているTerraformバージョンのドキュメントで`format_version`フィールドを確認し、想定するスキーマと一致するかをチェックすることをおすすめします。

**Q3. 大量のリソースがある構成でPlanの実行・レビューを高速化する方法はありますか?**

まず`-parallelism`オプションでAPI呼び出しの並列数を調整できますが、ネットワークやAPIレートリミットとのトレードオフがあるため闇雲に上げるのは禁物です。本質的な解決策としては、モジュール単位・環境単位でStateを分割し、変更があった範囲だけをPlan対象にすることです。CI側では、変更されたディレクトリを検出して該当モジュールのみPlanを実行する差分検出ロジック(例: `tj-actions/changed-files`など)を組み合わせると、不要なPlan実行を減らせます。
