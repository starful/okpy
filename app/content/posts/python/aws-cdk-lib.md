---
title: 'AWS CDKで始めるInfrastructure as Code実践ガイド（aws-cdk-lib）'
date: 2026-11-17
category: python
slug: aws-cdk-lib
summary: '- `aws-cdk-lib` はAWSの各種リソースをTypeScript/Pythonなどの汎用言語で定義できるIaCフレームワークの中核ライブラリで、CloudFormationテンプレートを裏側で生成する - `cdk init` でプロジェクトを作成し、Stack内でL2コンストラクトを組み合わせるだけ…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261117110221.jpg'
lang: ja
---

# AWS CDKで始めるInfrastructure as Code実践ガイド（aws-cdk-lib）

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261117110221.jpg)


## TL;DR

- `aws-cdk-lib` はAWSの各種リソースをTypeScript/Pythonなどの汎用言語で定義できるIaCフレームワークの中核ライブラリで、CloudFormationテンプレートを裏側で生成する
- `cdk init` でプロジェクトを作成し、Stack内でL2コンストラクトを組み合わせるだけで、VPCやLambda、S3などの実務構成を数十行で記述できる
- 本番運用では `cdk diff` によるレビュー、環境分離（Stage/Context）、IAM最小権限の明示化が事故防止の鍵になる

## 概要

AWS CDK（Cloud Development Kit）は、AWSのクラウドリソースをプログラミング言語でモデリングし、最終的にCloudFormationテンプレートへ変換（synth）してデプロイするIaCツールキットです。`aws-cdk-lib` はCDK v2で提供される単一の統合ライブラリで、EC2・S3・Lambda・ECS・RDSなど、AWSの主要サービスに対応するコンストラクトをすべて内包しています。

CDKのコンストラクトには3つの抽象度があります。

- **L1（CfnXxx）**: CloudFormationリソースをそのままラップしたもの。柔軟だが冗長
- **L2（Xxx）**: AWSのベストプラクティスを組み込んだ高レベルAPI。多くの場合これを使う
- **L3（Patterns）**: 複数サービスを組み合わせた構成パターン（例: ECSのロードバランス付きサービス一式）

Terraformなど宣言的なHCLと比較して、CDKはループ・条件分岐・関数・クラス継承といった言語機能をそのままIaCに持ち込める点が最大の特徴です。環境ごとの差分やモジュール化をコードとして自然に表現できるため、大規模な組織でのプラットフォーム化に向いています。

## インストール

Pythonで利用する場合、Node.js（CDK CLI自体がNode.js製）とPython両方の準備が必要です。

```bash
# CDK CLI（Node.js経由でグローバルインストール）
npm install -g aws-cdk

# プロジェクト用の仮想環境
python3 -m venv .venv
source .venv/bin/activate

# aws-cdk-lib と constructs（CDKの基盤ライブラリ）
pip install aws-cdk-lib constructs

# バージョン確認
cdk --version
```

新規プロジェクトは `cdk init` で初期化します。

```bash
mkdir my-cdk-app && cd my-cdk-app
cdk init app --language python
source .venv/bin/activate
pip install -r requirements.txt
```

AWS認証情報（`~/.aws/credentials` や環境変数）が設定済みであることを前提に、初回のみブートストラップを実行します。

```bash
cdk bootstrap aws://<account-id>/<region>
```

ブートストラップはCDKのデプロイに必要なS3バケットやIAMロードなどを作成する一度限りの処理で、アカウント・リージョンごとに1回だけ実行すれば十分です。

## 基本サンプル

### 最小構成：S3バケットとLambda

実務でよくある「S3にアップロードされたファイルをLambdaで処理する」構成を例にします。

```python
# app.py
from aws_cdk import App
from my_stack import MyServiceStack

app = App()
MyServiceStack(app, "MyServiceStack",
    env={"account": "123456789012", "region": "ap-northeast-1"}
)
app.synth()
```

```python
# my_stack.py
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_notifications as s3n,
)
from constructs import Construct


class MyServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self, "UploadBucket",
            bucket_name="my-service-uploads-dev",
            removal_policy=RemovalPolicy.DESTROY,  # 検証環境のみ想定
            auto_delete_objects=True,
            versioned=True,
        )

        handler = _lambda.Function(
            self, "ProcessUploadFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.main",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
            },
        )

        # バケットへの読み取り権限をLambdaに自動付与（IAMポリシーを明示不要）
        bucket.grant_read(handler)

        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(handler),
            s3.NotificationKeyFilter(suffix=".csv"),
        )
```

`bucket.grant_read(handler)` のように、L2コンストラクトは権限付与を1行で表現できます。内部的には最小限のIAMポリシーステートメントが自動生成されるため、手書きのIAM JSONを書く必要がありません。

### デプロイとレビューの流れ

```bash
# CloudFormationテンプレートを生成して確認
cdk synth

# 現在のデプロイ済み状態との差分を確認（最重要）
cdk diff

# デプロイ
cdk deploy --require-approval broadening

# 不要になったら削除
cdk destroy
```

`cdk diff` は、IAM権限の変更やセキュリティグループの変更など「破壊的・影響範囲の広い変更」を事前にレビューできる最も重要なコマンドです。CI/CDパイプラインに組み込み、PRの段階で差分を可視化する運用が推奨されます。

### 環境分離（dev/prod）の実践例

```python
# app.py
from aws_cdk import App
from my_stack import MyServiceStack

app = App()

envs = {
    "dev": {"account": "111111111111", "region": "ap-northeast-1"},
    "prod": {"account": "222222222222", "region": "ap-northeast-1"},
}

stage = app.node.try_get_context("stage") or "dev"

MyServiceStack(
    app, f"MyServiceStack-{stage}",
    env=envs[stage],
    stack_name=f"my-service-{stage}",
)

app.synth()
```

```bash
cdk deploy -c stage=prod
```

コンテキスト変数（`-c`）でステージを切り替えることで、同じコードベースから複数環境のスタックを安全に管理できます。本番用の値を `cdk.json` にハードコードしないよう注意してください。

## 注意点

1. **`RemovalPolicy.DESTROY` の誤用に注意**
   S3バケットやRDSインスタンスなどステートフルなリソースに `RemovalPolicy.DESTROY` を設定したまま本番適用すると、`cdk destroy` やスタック更新時に意図せずデータが削除されます。本番環境では `RemovalPolicy.RETAIN`（既定値）を維持し、検証環境のみ明示的にDESTROYを指定するのが安全です。

2. **ブートストラップのバージョン不整合**
   古いバージョンでブートストラップしたアカウントに新しいCDK CLIでデプロイすると、`This stack uses assets, so the toolkit stack version must be...` のようなエラーが発生します。CI環境とローカル環境でCDK CLIのバージョンを固定（`package.json` や `requirements.txt` でピン留め）することを推奨します。

3. **論理IDの変更によるリソース再作成**
   コンストラクトID（`self, "UploadBucket"` の部分）を変更すると、CloudFormation上の論理IDが変わり、既存リソースが削除されて新規作成される場合があります。特にRDSやDynamoDBなどデータを持つリソースでは、IDのリネームは `cdk diff` で必ず事前確認してください。

4. **Lambdaアセットのサイズとコールドスタート**
   `_lambda.Code.from_asset("lambda")` でディレクトリ全体をZIP化するため、不要な依存ライブラリが混在するとデプロイが遅くなるだけでなく、コールドスタートにも影響します。依存関係は `aws_lambda_python_alpha` の `PythonFunction` を使うか、Dockerバンドリングで最小化することを検討してください。

5. **カスタムリソースとデプロイ時間**
   Custom ResourceやLambda-backed Providerを多用すると、`cdk deploy` の実行時間が大幅に伸びることがあります。可能な限りAWS標準のL2コンストラクトで表現できないか先に検討しましょう。

## FAQ

**Q1. CDKとTerraformはどちらを選ぶべきですか？**
AWS単一クラウドに限定され、チームがTypeScript/Python/Javaなどの言語に慣れている場合はCDKが生産性で優位です。マルチクラウドやベンダー中立性を重視する場合、あるいは既存のTerraformモジュール資産がある場合はTerraformが適しています。両者を併用し、新規AWS専用プロジェクトのみCDKで構築する折衷策もよく採られます。

**Q2. `cdk deploy` が `Resource creation cancelled` で失敗するのはなぜですか？**
多くの場合、スタック内の他のリソース作成が失敗したためにCloudFormationが並行作成中のリソースをロールバックしたことが原因です。実際のエラーはCloudFormationコンソールのイベントタブ、またはCLIで次のコマンドから確認できます。

```bash
aws cloudformation describe-stack-events \
  --stack-name MyServiceStack-dev \
  --max-items 20
```

多くはIAM権限不足、サービスクォータ超過、既存リソースとの名前衝突が原因です。

**Q3. 複数のスタックで共通のVPCやKMSキーを再利用したい場合はどうすればよいですか？**
`CfnOutput` でエクスポートした値を他スタックが参照するクロススタック参照、または `Fn.import_value` を使う方法がありますが、依存関係が密結合になりスタック削除順序に制約が生じます。実務では、共有リソース（VPCなど）を専用の「Foundationスタック」として分離し、`ssm.StringParameter` にARNやIDを保存して他スタックから `StringParameter.value_from_lookup` で参照する構成がより運用しやすいです。

```python
# Foundationスタック側
ssm.StringParameter(
    self, "VpcIdParam",
    parameter_name="/shared/vpc-id",
    string_value=vpc.vpc_id,
)
```

```python
# 利用側スタック
vpc_id = ssm.StringParameter.value_from_lookup(self, "/shared/vpc-id")
```

---

CDKは「AWSリソースをコードで表現する」ことの敷居を大きく下げますが、裏側で生成されるCloudFormationの挙動（置換・ロールバック・削除保護）を理解していないと、便利さと裏腹に事故を起こしやすいツールでもあります。まずは検証環境で `cdk diff` を習慣化し、ステートフルなリソースの削除ポリシーを常に意識することが、実務で安全に使いこなす第一歩になります。
