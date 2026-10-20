---
title: 'Terraform plan with -target flag: スコープ適用のリスクとロールバック戦略'
date: 2026-10-20
category: terraform
slug: terraform-plan-with-target-flag-scoped-apply-risks-and-rollback-strategies
summary: 'Terraform を運用していると、「このリソースだけ先に反映したい」「大規模な plan のうち一部だけ検証したい」という場面に必ず遭遇します。そこで使われるのが `-target` フラグです。便利な反面、使い方を誤ると state の整合性が崩れ、思わぬリソース削除やドリフトを引き起こす危険なオプションで…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261020185132.jpg'
lang: ja
---

# Terraform plan with -target flag: スコープ適用のリスクとロールバック戦略

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261020185132.jpg)


Terraform を運用していると、「このリソースだけ先に反映したい」「大規模な plan のうち一部だけ検証したい」という場面に必ず遭遇します。そこで使われるのが `-target` フラグです。便利な反面、使い方を誤ると state の整合性が崩れ、思わぬリソース削除やドリフトを引き起こす危険なオプションでもあります。本記事では `-target` の概念から HCL 例、state への影響、モジュール構成での挙動、注意点、そしてロールバック戦略までを実践的にまとめます。

## 1. `-target` フラグとは何か

`terraform plan -target=<リソースアドレス>` や `terraform apply -target=<リソースアドレス>` は、Terraform の依存関係グラフ全体を評価するのではなく、指定したリソース（および、そのリソースが依存しているリソース）だけに操作対象を絞り込む機能です。

```bash
terraform plan -target=aws_instance.web
terraform apply -target=module.network.aws_vpc.main
```

Terraform 内部では、通常の実行は「リソース依存グラフ全体を走査して差分を計算する」のが前提です。`-target` を指定すると、Terraform はそのグラフのうち指定ノードとその上流（依存先）だけを残したサブグラフを作り、それ以外は評価対象から除外します。つまり「下流（そのリソースに依存している他のリソース）」は基本的に無視されます。

これは本来、次のような**緊急時のデバッグ**や**段階的な初期構築**を想定した機能です。

- 巨大な plan が失敗し、原因となっているリソースだけを先に直したい
- 新規構築時に、VPC → サブネット → EC2 のように順序立てて確認しながら適用したい
- state が壊れた一部のリソースだけを再作成して切り離したい

公式ドキュメントでも「通常のワークフローでは使うべきではない」「デバッグ用の例外的機能」と明記されており、常用を前提にした機能ではない点をまず理解しておく必要があります。

## 2. HCL 例で見る `-target` の挙動

以下のような典型的な VPC + EC2 構成を例にします。

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_instance" "web" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
  subnet_id      = aws_subnet.public.id

  tags = {
    Name = "web-server"
  }
}

resource "aws_eip" "web_eip" {
  instance = aws_instance.web.id
  domain   = "vpc"
}
```

ここで `terraform apply -target=aws_instance.web` を実行すると、Terraform は以下のように動作します。

1. `aws_instance.web` が依存する `aws_subnet.public`、さらにその依存元の `aws_vpc.main` は評価・作成されます（上流は含まれる）。
2. `aws_instance.web` 自体も作成されます。
3. しかし `aws_eip.web_eip` は `aws_instance.web` に依存している「下流」のリソースなので、**対象外**となり作成されません。

つまり `-target` は「指定したリソースに到達するために必要なものは連れてくるが、指定したリソースから先に進んだ依存関係は無視する」という一方向的な絞り込みです。この非対称性を理解していないと、「EIP が付与されていない」「セキュリティグループのルールが反映されていない」といった不整合に気づかず本番適用してしまうことがあります。

複数リソースを同時指定する場合はフラグを繰り返します。

```bash
terraform apply -target=aws_vpc.main -target=aws_subnet.public
```

## 3. state への影響

`-target` を使った apply は、通常の apply と同様に state ファイルを更新します。ここで注意すべきは、**plan に含まれなかったリソースの state は更新されない**という点です。

例えば、モジュール内部で変数の変更が複数リソースに影響する設計になっている場合、`-target` で一部のリソースだけ適用すると、state 上は「反映済み」のリソースと「古い定義のまま」のリソースが混在する状態になります。この状態で後日 `terraform plan`（ターゲットなし）を実行すると、以下のような差分が大量に出ることがあります。

```
Terraform will perform the following actions:

  # aws_security_group.app will be updated in-place
  ~ resource "aws_security_group" "app" {
      ...
    }

Plan: 3 to add, 5 to change, 1 to destroy.
```

この「意図していない差分」は、`-target` 適用時に見ていなかった下流リソースが後からまとめて検出された結果です。レビュー担当者が差分の意味を正しく説明できないまま apply してしまうと、本番環境に予期しない変更が入るリスクがあります。

また `-target` には `-replace` と組み合わせるパターンもあります。

```bash
terraform apply -replace="aws_instance.web" -target=aws_instance.web
```

これは「特定リソースだけを強制的に再作成する」操作で、state 上は destroy → create として記録されます。EIP のように他リソースに依存されているリソースを対象にすると、関連付けが一時的に外れたまま apply が完了してしまうケースもあるため、`-replace` と `-target` の併用は特に慎重に扱う必要があります。

## 4. モジュール構成での `-target` の指定方法と注意

モジュールを使っている場合、`-target` はモジュールのパスを含めて指定します。

```bash
# モジュール全体を対象にする
terraform apply -target=module.network

# モジュール内の特定リソースを対象にする
terraform apply -target=module.network.aws_subnet.public

# for_each / count を使っているリソースのインスタンス単位で指定
terraform apply -target='module.ec2["web"]'
terraform apply -target='aws_instance.web[0]'
```

モジュール単位で `-target` を指定すると、そのモジュール内のすべてのリソースが対象になります。モジュールが他モジュールの出力（output）を参照している場合、その参照元モジュールのリソースも上流として自動的に含まれます。

注意点として、モジュールをネストしている構成では `-target` のアドレス解釈が複雑になりやすく、意図したリソースだけが対象になっているかを `plan` の出力でしっかり確認する必要があります。特に `for_each` でリソースが動的に生成される場合、インデックスやキーを誤って指定すると「対象が0件」のまま plan が完了し、何も変更されていないのに安心してしまうミスが起こりやすいです。

```bash
terraform plan -target='module.ec2["staging"]'
```

このように、必ず `plan` の末尾に表示される `Plan: X to add, Y to change, Z to destroy.` の数値を確認し、想定した件数と一致しているかをチェックする習慣をつけることが重要です。

## 5. `-target` 運用時の注意点

### 5.1 常用を避ける

`-target` は本来、設定ファイル（.tf）側の依存関係グラフでは本質的な解決にならない「その場しのぎ」の手段です。同じ `-target` 指定を繰り返し使っている場合は、モジュール分割や `depends_on` の見直し、あるいはリソース自体の設計を見直すべきサインです。

### 5.2 CI/CD パイプラインでの使用は原則禁止

自動化された CI/CD パイプラインに `-target` をハードコードすると、将来的にリソース構成が変わった際に「対象外リソースが永久に反映されない」状態が固定化されます。緊急対応で一時的に使った場合は、必ず次のステップでターゲットなしの `plan`/`apply` を実行し、差分がゼロになることを確認してからパイプラインを正常化してください。

### 5.3 チーム内での合意形成

`-target` を使った apply はレビュー者にとって「全体像が見えない変更」になりがちです。Pull Request のレビューで plan 全体を提示できないため、チームでは「`-target` 適用時は Slack やチケットに理由と対象範囲を明記する」といった運用ルールを設けることを推奨します。

### 5.4 destroy との併用は特に危険

```bash
terraform destroy -target=aws_instance.web
```

`destroy -target` は、指定リソースに依存している下流リソース（EIP、ALB ターゲットグループのアタッチメントなど）も合わせて削除対象に含める場合があります。`apply -target` とは逆に、destroy では依存関係の扱いが広がる方向に働くため、「このリソースだけ消すつもりが、関連する複数リソースまで一緒に消えた」という事故が起こりやすいです。実行前に必ず `terraform plan -destroy -target=...` で削除予定リストを確認してください。

## 6. ロールバック戦略

`-target` 適用後に問題が発覚した場合のロールバック手段を整理します。

### 6.1 state のバックアップからの復元

Terraform は `terraform apply` 実行時に自動でローカルの `terraform.tfstate.backup` を生成します（ローカル state の場合）。S3 バックエンドなど remote state を使っている場合は、バージョニングを有効にしておくことで直前の state バージョンに戻せます。

```bash
# S3 バージョニングを使ったロールバック例
aws s3api list-object-versions --bucket my-tfstate-bucket --prefix env/prod/terraform.tfstate

aws s3api get-object \
  --bucket my-tfstate-bucket \
  --key env/prod/terraform.tfstate \
  --version-id <直前のバージョンID> \
  terraform.tfstate.rollback

terraform state push terraform.tfstate.rollback
```

### 6.2 ターゲットを逆方向に指定して戻す

`-target` で加えた変更を打ち消す場合、設定ファイル側を元の記述に戻した上で、同じリソースに対して再度 `-target` を指定して apply します。

```bash
# HCL を変更前の状態に git revert してから
git revert <コミットハッシュ>
terraform apply -target=aws_instance.web
```

これは state のバージョン管理に依存しない「設定ベースのロールバック」であり、state ファイル自体を直接操作しないため比較的安全です。

### 6.3 全体 plan での整合性チェックを必須化

ロールバック後は、必ずターゲットを外した `terraform plan` を実行し、差分がゼロであることを確認します。差分が残っている場合、`-target` 適用によって他のリソースにも波及していた可能性があるため、放置せず原因を特定してください。

```bash
terraform plan
# Plan: 0 to add, 0 to change, 0 to destroy. を確認する
```

### 6.4 `import` / `state rm` による整合性の再構築

`-target` と `-replace` の併用で state とクラウド側の実体が食い違ってしまった場合、`terraform state rm` で該当リソースを state から除外し、`terraform import` で現状のクラウドリソースを再登録する方法もあります。

```bash
terraform state rm aws_instance.web
terraform import aws_instance.web i-0123456789abcdef0
```

この手順は手動操作が多く誤りやすいため、可能であれば事前に state のバックアップを取得してから行ってください。

## 7. AWS / GCP / Azure との関係

`-target` 自体はクラウドプロバイダーに依存しない Terraform コア機能ですが、各クラウドのリソース依存の密度によってリスクの大きさが変わります。

- **AWS**: VPC、サブネット、セキュリティグループ、ALB、Auto Scaling Group など相互参照が多く、`-target` で一部だけ適用すると Target Group Attachment や EIP の紐付けが漏れやすい傾向があります。
- **GCP**: `google_compute_instance` と `google_compute_network`、IAM バインディング（`google_project_iam_member` など）が密に連携しているため、`-target` 適用時に IAM 権限の反映漏れが起きると、後続のリソース作成がパーミッションエラーで失敗することがあります。
- **Azure**: リソースグループ単位でのライフサイクル管理が前提になっているため、`-target` でリソースグループ配下の一部だけを操作すると、ARM テンプレート的な「一括デプロイ」の思想とズレが生じやすく、Azure Policy による準拠チェックに引っかかることがあります。

いずれのクラウドでも共通して言えるのは、「マネージドリソース同士の暗黙的な依存（IAM、ネットワーク、ロードバランサーの紐付けなど）」が `-target` の対象外になりやすく、これが事故の主な原因になるという点です。

## 8. FAQ

**Q1. `-target` を使うと、state ファイルは壊れますか？**

A. `-target` 自体が state を直接破壊するわけではありません。Terraform は対象リソースについて正しく state を更新します。問題が起きるのは「対象外リソースの state が古いままになり、設定ファイルと state の間に見えないズレが生じる」ことです。定期的にターゲットなしの `plan` を実行して差分を確認すれば、ズレを早期に検知できます。

**Q2. `-target` の代わりに使える、より安全な方法はありますか？**

A. 構成を小さなモジュール・ワークスペースに分割し、`terraform plan` の対象範囲自体を小さく保つのが最も安全な代替策です。また、一時的な依存の解決が目的であれば `depends_on` を明示することで、`-target` に頼らずに正しい適用順序を Terraform に理解させられます。緊急時のデバッグ目的以外では `-target` を使わない設計を目指すべきです。

**Q3. CI/CD で誤って `-target` 付きの apply が実行されてしまった場合、何を確認すべきですか？**

A. まず該当パイプラインの実行ログから対象リソースを特定し、ターゲットなしの `terraform plan` を実行して全体の差分を確認します。差分がある場合は、その内容がチームの意図した変更か、`-target` 適用の副作用かを切り分けます。意図しない差分であれば、本記事のロールバック戦略（設定の revert + 再適用、または state バックアップからの復元）に従って対応し、再発防止のためパイプライン側で `-target` の使用を禁止するバリデーション（例: `terraform plan` の引数チェック）を追加することを推奨します。

---

`-target` は Terraform が提供する「緊急脱出用レバー」であり、日常的な運用フローに組み込むべき機能ではありません。使う場合は、対象範囲と依存関係の非対称性を正しく理解し、適用後には必ずターゲットなしの `plan` で整合性を確認する——この一手間が、state の静かな破綻を防ぐ最も確実な方法です。
