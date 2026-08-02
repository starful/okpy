---
title: 'Terraform lifecycle hooks と リソース管理のベストプラクティス'
date: 2026-08-01
category: terraform
slug: terraform-lifecycle-hooks-and-resource-management-best-practices
summary: 'Terraform を使ったインフラ管理を長く続けていると、リソースの再作成による意図しないダウンタイムや、`terraform destroy` による誤削除など、運用上のリスクに直面する場面が増えてきます。こうした問題に対処するための仕組みが `lifecycle` ブロックです。本記事では `lifecyc…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20260801100617.jpg'
lang: ja
---

# Terraform lifecycle hooks と リソース管理のベストプラクティス

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20260801100617.jpg)


Terraform を使ったインフラ管理を長く続けていると、リソースの再作成による意図しないダウンタイムや、`terraform destroy` による誤削除など、運用上のリスクに直面する場面が増えてきます。こうした問題に対処するための仕組みが `lifecycle` ブロックです。本記事では `lifecycle` の各サブブロックの概念、実際の HCL 例、state との関係、モジュール設計での注意点までを一気通貫で解説します。

## lifecycle ブロックとは何か

Terraform の各リソースブロック内には、リソースの作成・更新・削除の挙動を制御するための `lifecycle` ブロックを記述できます。これは特定のプロバイダー(AWS/GCP/Azure など)に依存しない、Terraform コア自体が提供する機能です。つまり `aws_instance` でも `google_compute_instance` でも `azurerm_linux_virtual_machine` でも、書き方はまったく同じです。

主なサブブロックは次の4つです。

- `create_before_destroy` — リソースを削除する前に新しいリソースを作成する
- `prevent_destroy` — `terraform destroy` やリソース定義の削除による破棄を防ぐ
- `ignore_changes` — 指定した属性の変更を plan/apply で無視する
- `replace_triggered_by` — 指定したリソースや属性が変化した際に強制的に再作成する

これらを適切に組み合わせることで、「意図しない再作成」「意図しない削除」「外部要因による差分検出」といった Terraform 運用でよくある悩みをコントロールできます。

## create_before_destroy

デフォルトでは、Terraform は属性変更によってリソースの再作成(destroy → create)が必要になった場合、先に既存リソースを破棄してから新しいリソースを作成します。これは Auto Scaling Group や Launch Template、DNS レコードなど、ダウンタイムを避けたいリソースにとっては致命的です。

```hcl
resource "aws_launch_template" "app" {
  name_prefix   = "app-"
  image_id      = var.ami_id
  instance_type = "t3.medium"

  lifecycle {
    create_before_destroy = true
  }
}
```

`name_prefix` を使っているのがポイントです。`create_before_destroy = true` の場合、新旧のリソースが一時的に共存するため、`name` のような一意制約のある属性をそのまま使うと名前衝突でエラーになります。`name_prefix` でランダムなサフィックスを付与することで衝突を回避します。

Auto Scaling Group と組み合わせる場合は、参照する Launch Template 側にこの設定を入れておくのが定石です。

## prevent_destroy

本番環境のデータベースやステートフルなストレージなど、誤って削除されると致命的なリソースには `prevent_destroy` を設定します。

```hcl
resource "aws_db_instance" "prod" {
  identifier        = "prod-db"
  engine            = "postgres"
  instance_class    = "db.r6g.large"
  allocated_storage = 100

  lifecycle {
    prevent_destroy = true
  }
}
```

この設定があると、`terraform destroy` の実行はもちろん、HCL からこのリソースブロック自体を削除して `apply` した場合もエラーになり、削除が阻止されます。CI/CD パイプラインでの誤操作を防ぐ最後の砦として、本番の重要リソースには必ず設定しておくべきです。

ただし注意点として、`prevent_destroy` は値に変数を渡すことができません(リテラルの `true`/`false` のみ)。環境ごとに切り替えたい場合は、`count` や別ファイルでのオーバーライド、あるいは workspace ごとに異なるモジュール呼び出しを検討する必要があります。

## ignore_changes

外部システム(オートスケーリングによるインスタンス数の変動、手動でのタグ付け、CI が自動更新するイメージタグなど)によって Terraform 管理外で変更される属性がある場合、`ignore_changes` でその属性を無視できます。

```hcl
resource "aws_autoscaling_group" "app" {
  name             = "app-asg"
  desired_capacity = 2
  min_size         = 2
  max_size         = 10
  vpc_zone_identifier = var.subnet_ids

  lifecycle {
    ignore_changes = [desired_capacity]
  }
}
```

この例では、Auto Scaling によって `desired_capacity` が変動しても、次回の `plan` でその差分がドリフトとして検出されなくなります。

全属性を無視したい場合は `ignore_changes = all` も指定可能ですが、これは事実上そのリソースを Terraform の管理外に置くのと同義であり、多用すると構成の追跡ができなくなるため慎重に使うべきです。

## replace_triggered_by (Terraform 1.2+)

特定のリソースや値が変化したときに、明示的に別リソースの再作成を強制したい場合に使います。

```hcl
resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = "t3.medium"

  lifecycle {
    replace_triggered_by = [
      aws_launch_template.app.id
    ]
  }
}
```

以前は `null_resource` と `triggers` を組み合わせたハック的な方法が使われていましたが、`replace_triggered_by` によってネイティブにこの依存関係を表現できるようになりました。

## state との関係

`lifecycle` ブロックの挙動は state ファイル(`terraform.tfstate`)の扱いと密接に関係しています。

- `create_before_destroy` を使うと、apply の過程で一時的に新旧2つのリソースが state 上に存在します。apply が正常に完了すれば旧リソースは state からも実インフラからも削除されます。
- `prevent_destroy` はあくまで plan/apply レベルでの防御であり、`terraform state rm` によって state からリソースを切り離すこと自体は防げません。state 操作は別途 IAM/権限や CI 承認フローで制御する必要があります。
- `ignore_changes` は state 上の値と実際のリソースの値に差異があっても、その差異を無視して比較対象から除外する仕組みです。state 自体の値は `refresh` 時に更新されますが、次回 plan での差分検出には反映されません。

state はチームで共有されるため、S3 + DynamoDB(AWS)、GCS(GCP)、Azure Storage Account(Azure)などのリモートバックエンドを使い、ロックとバージョニングを有効にしておくことが前提条件になります。`lifecycle` の設定ミスによる意図しない destroy/create は、state のバージョン管理があれば復旧の手がかりになります。

## モジュールでの注意点

モジュールを設計する際、`lifecycle` ブロックにはいくつか制約があります。

1. **変数を直接渡せない**: `prevent_destroy` や `create_before_destroy` の真偽値には変数参照(`var.xxx`)を使えません。これは Terraform の言語仕様上の制約で、lifecycle の値は静的に解決可能でなければならないためです。環境ごとに切り替えたい場合は、モジュールを条件分岐せずに呼び出し側で `count = var.prevent_destroy ? 1 : 0` のような形で別リソース定義を用意するなどの工夫が必要です。
2. **`ignore_changes` はモジュール内で固定される**: モジュールの利用者が `ignore_changes` の対象属性を外部からカスタマイズすることはできません。柔軟性が必要な場合は、モジュール自体を分割するか、attribute のリストをモジュール内で条件付きにする設計を検討します。
3. **継承されない**: 親モジュールで `lifecycle` を設定しても、子モジュール内のリソースには自動的に継承されません。各リソースごとに明示的な設定が必要です。

モジュールの再利用性を高めたい場合は、「本当にそのリソース固有の lifecycle 設定が必要か」「呼び出し側で制御すべきか」を設計段階で切り分けておくと、後々のメンテナンスコストが下がります。

## クラウドプロバイダーごとの関係

`lifecycle` ブロック自体は Terraform コアの機能であり、AWS・GCP・Azure のどのプロバイダーでも同じ構文で使えます。ただし実際に効果的な使い所はリソースの性質によって異なります。

- **AWS**: `aws_launch_template`、`aws_autoscaling_group`、`aws_db_instance`、Route53 のレコードなど、置き換えにダウンタイムが伴うリソースで `create_before_destroy` がよく使われます。
- **GCP**: `google_compute_instance_template` や `google_sql_database_instance` など、AWS と同様の考え方が適用できます。特に Cloud SQL インスタンスは削除保護のためのプロバイダー独自属性(`deletion_protection`)も持っており、`prevent_destroy` と併用されることが多いです。
- **Azure**: `azurerm_linux_virtual_machine_scale_set` や `azurerm_mssql_server` などでも同様のパターンが有効です。Azure の一部リソースには `lifecycle { ignore_changes }` を使わないと、ポータルからの手動変更のたびにドリフトが検出されてしまうケースがあります(タグの自動付与など)。

いずれのクラウドでも共通するのは、「プロバイダー固有の削除保護属性(`deletion_protection` 等)」と「Terraform コアの `lifecycle` ブロック」は別レイヤーの仕組みであり、両方を組み合わせて多層防御にするのが望ましいという点です。

## 実務上の注意点まとめ

- `create_before_destroy` を使う際は、一意制約のある名前系属性(`name` など)を `name_prefix` や `random_id` と組み合わせて衝突を回避する。
- `prevent_destroy` は本番の重要リソースにはデフォルトで付与する運用ルールをチームで統一する。ただし state 操作自体は防げないため、CI/CD 側での承認フローと併用する。
- `ignore_changes = all` の乱用はドリフト検出を無効化してしまうため、必要最小限の属性リストに絞る。
- `lifecycle` の変更(特に `create_before_destroy` の追加・削除)は plan の内容が大きく変わることがあるため、必ず `terraform plan` の出力を確認してから apply する。
- CI 上で `terraform plan` の差分を目視レビューする文化を維持し、`-auto-approve` を本番環境では使わない。

## FAQ

**Q1. `prevent_destroy = true` を設定しているのに `terraform destroy` が通ってしまいました。なぜですか?**

考えられる原因はいくつかあります。まず、`lifecycle` ブロックの記述ミス(インデントやリソースブロックの外に書いてしまっている)がないか確認してください。次に、対象のリソース定義自体が `count = 0` や `for_each` の空マップによって作成対象から除外されていないかを確認します。Terraform は plan の対象に含まれないリソースについては `prevent_destroy` の評価自体を行わないため、意図せず対象外になっているケースが典型的な原因です。

**Q2. `create_before_destroy` を設定したら、依存している他のリソースでエラーが出るようになりました。**

`create_before_destroy` を有効にしたリソースに依存する他のリソースがある場合、それらのリソースにも暗黙的に `create_before_destroy` の依存関係が波及することがあります。例えばセキュリティグループを `create_before_destroy` にした場合、それを参照するリソース側で一意制約違反や依存関係の循環が起きることがあります。この場合、依存先のリソースにも同様に `create_before_destroy` を設定するか、`depends_on` を明示して作成順序を制御する必要があります。

**Q3. `ignore_changes` を設定した属性を、どうしても一度だけ Terraform 側の値で強制上書きしたい場合はどうすればよいですか?**

`ignore_changes` は静的な設定のため、一時的に解除することはできません。対処法としては、(1) 該当リソースを `terraform apply -target` で一時的に対象化しつつ、HCL 側で一時的に `ignore_changes` を削除して apply する、(2) `terraform state rm` で state から切り離した後に `terraform import` で最新の実体を取り込み直す、のいずれかが一般的です。ただしどちらも一時的な HCL 変更やコマンド操作が伴うため、変更履歴が追いにくくなる点に注意し、作業後は必ず `ignore_changes` の設定を元に戻してください。

---

`lifecycle` ブロックは小さな機能ですが、正しく使うことで「ゼロダウンタイムでのリソース入れ替え」「本番リソースの誤削除防止」「外部変更によるドリフトの抑制」を実現できます。一方で、変数を渡せない・モジュールに継承されないといった制約もあるため、チームのインフラ構成に合わせてどこまでモジュール化し、どこを呼び出し側の責務にするかを設計段階で明確にしておくことが、長期的な運用のしやすさにつながります。
