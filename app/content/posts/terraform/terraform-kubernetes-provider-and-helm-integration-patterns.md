---
title: 'Terraform で構築する Kubernetes Provider と Helm 連携パターン実践ガイド'
date: 2026-09-26
category: terraform
slug: terraform-kubernetes-provider-and-helm-integration-patterns
summary: 'Terraform は infrastructure as code の代表的なツールとして、クラウド上のインフラ構築に広く使われています。近年ではその適用範囲が Kubernetes クラスタの中身、すなわちマニフェストや Helm チャートのデプロイにまで拡大しており、`kubernetes` provide…'
lang: ja
---

# Terraform で構築する Kubernetes Provider と Helm 連携パターン実践ガイド

## はじめに

Terraform は infrastructure as code の代表的なツールとして、クラウド上のインフラ構築に広く使われています。近年ではその適用範囲が Kubernetes クラスタの中身、すなわちマニフェストや Helm チャートのデプロイにまで拡大しており、`kubernetes` provider と `helm` provider を組み合わせることで、クラスタの作成からアプリケーションのデプロイまでを単一のワークフローで管理するパターンが定着しつつあります。本記事では、この 2 つの provider を使ったインフラパターンについて、概念、HCL 実装例、state 管理、モジュール化、注意点、FAQ の順で解説します。

## 概念整理

### なぜ Terraform で Kubernetes リソースを管理するのか

Kubernetes には kubectl や kustomize、Argo CD、Flux といった専用のデプロイツールが存在しますが、Terraform で管理するメリットは主に以下の点にあります。

- クラウド側のリソース(EKS/GKE/AKS クラスタ、VPC、IAM、ノードグループなど)と Kubernetes 内部リソース(Namespace、Deployment、Helm リリースなど)を **同一の state とワークフローで一元管理** できる
- `terraform plan` によって変更の差分を事前に可視化できる
- モジュール化によってマルチ環境・マルチクラスタでの再利用性が高まる

一方で、GitOps ツールのような継続的同期は苦手であり、頻繁に変更されるアプリケーションレイヤーのデプロイには不向きな面もあります。この使い分けの判断が設計上の重要なポイントになります。

### kubernetes provider と helm provider の役割分担

- **kubernetes provider**: `kubernetes_manifest`、`kubernetes_deployment`、`kubernetes_namespace` などのリソースを使い、Kubernetes API に対して直接マニフェストを適用する
- **helm provider**: `helm_release` リソースを通じて Helm チャートをデプロイし、values の管理やアップグレード・ロールバックを Terraform のライフサイクルに統合する

多くの実務パターンでは、Namespace や RBAC、Secret といった軽量なリソースは kubernetes provider で、Ingress Controller や Prometheus、cert-manager といった複雑なコンポーネントは helm provider で管理する、という棲み分けが行われます。

## クラスタ構築から Provider 設定までの流れ

kubernetes / helm provider を使う前提として、クラスタの認証情報を Terraform に渡す必要があります。マネージドクラスタ(EKS/GKE/AKS)を同一の Terraform 構成内で作成する場合、provider の設定はクラスタリソースの出力値に依存する形になります。

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.31"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.14"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_eks_cluster_auth" "this" {
  name = module.eks.cluster_name
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.this.token
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.this.token
  }
}
```

このように EKS モジュールの出力(エンドポイント、CA 証明書)を kubernetes/helm provider の設定に渡すことで、クラスタ作成とアプリケーションデプロイを 1 回の `terraform apply` で完結させられます。ただし後述するように、この「1 apply 方式」には注意点もあります。

## HCL 実装例

### Namespace と RBAC を kubernetes provider で管理する

```hcl
resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
    labels = {
      "managed-by" = "terraform"
    }
  }
}

resource "kubernetes_service_account" "monitoring_sa" {
  metadata {
    name      = "monitoring-sa"
    namespace = kubernetes_namespace.monitoring.metadata[0].name
  }
}
```

### Helm チャートで Ingress Controller をデプロイする

```hcl
resource "helm_release" "ingress_nginx" {
  name       = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  version    = "4.11.2"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name

  values = [
    yamlencode({
      controller = {
        replicaCount = 2
        service = {
          type = "LoadBalancer"
        }
        resources = {
          requests = {
            cpu    = "100m"
            memory = "128Mi"
          }
        }
      }
    })
  ]

  set {
    name  = "controller.metrics.enabled"
    value = "true"
  }
}
```

`values` には `yamlencode()` を使うことで、Terraform 変数と Helm values.yaml の構造を型安全に対応付けられます。細かい上書きは `set` ブロックを併用するのが実務上のバランスが良いパターンです。

### kubernetes_manifest でカスタムリソースを扱う

CRD を伴うリソース(cert-manager の `Certificate` など)は `kubernetes_manifest` で柔軟に定義できます。

```hcl
resource "kubernetes_manifest" "cert_issuer" {
  manifest = {
    apiVersion = "cert-manager.io/v1"
    kind       = "ClusterIssuer"
    metadata = {
      name = "letsencrypt-prod"
    }
    spec = {
      acme = {
        server = "https://acme-v02.api.letsencrypt.org/directory"
        email  = var.acme_email
        privateKeySecretRef = {
          name = "letsencrypt-prod-key"
        }
        solvers = [
          {
            http01 = {
              ingress = {
                class = "nginx"
              }
            }
          }
        ]
      }
    }
  }

  depends_on = [helm_release.cert_manager]
}
```

CRD 自体をインストールする Helm チャート(cert-manager本体)への `depends_on` を明示することで、CRD が存在しない状態で `kubernetes_manifest` が適用され失敗する事故を防げます。

## State 管理のポイント

kubernetes / helm リソースを Terraform state で扱う際は、通常のクラウドリソースとは異なる特有の注意が必要です。

- **state のリモート管理は必須**: S3+DynamoDB や Terraform Cloud、GCS など、チームで共有できるバックエンドを使い、ローカル state での運用は避ける
- **helm_release の state は Helm のリリース履歴と独立している**: Terraform state 上では単一リソースとして扱われるが、実体は Kubernetes クラスタ内の Secret(Helm リリース情報)にも保存されている。手動で `helm upgrade`/`helm rollback` を実行すると Terraform state とのドリフトが発生する
- **kubernetes_manifest はプラン時にクラスタへの接続が必要**: このリソースタイプは `terraform plan` の段階で対象リソースの現在の状態をクラスタから取得するため、クラスタが到達不能な状態(例えば初回作成中)だと plan 自体が失敗する。これが「1 apply でクラスタ作成とマニフェスト適用を同時に行う」構成の落とし穴になりやすい
- **state のインポート**: 既存クラスタに手動で入れた Helm リリースを Terraform 管理下に置く場合は `terraform import helm_release.example namespace/release-name` を使うが、values の差分が出やすいので import 後は必ず `terraform plan` で差分ゼロを確認する

## モジュール設計パターン

実務では、以下のような 3 層構成でモジュールを分割するケースが多く見られます。

```
modules/
├── cluster/       # EKS/GKE/AKS クラスタ本体、ノードグループ、ネットワーク
├── platform/      # kubernetes provider の namespace/RBAC、helm による共通コンポーネント
│                  # (ingress-nginx, cert-manager, external-dns, prometheus など)
└── workload/      # アプリケーション固有の helm_release やマニフェスト
```

クラスタ作成(cluster)とプラットフォームコンポーネント(platform)を別の state に分離し、`terraform_remote_state` データソースや、あるいは CI パイプライン上でクラスタの出力値をパラメータストア(SSM Parameter Store や GCP Secret Manager など)経由で受け渡す設計が、大規模環境では推奨されます。同一 state に混在させると、クラスタの small な変更(タグ更新など)でも kubernetes/helm リソース全体の plan 対象になり、レビューコストと apply のリスクが増大するためです。

```hcl
# platform 層での参照例
data "terraform_remote_state" "cluster" {
  backend = "s3"
  config = {
    bucket = "my-org-tfstate"
    key    = "cluster/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

provider "helm" {
  kubernetes {
    host                   = data.terraform_remote_state.cluster.outputs.cluster_endpoint
    cluster_ca_certificate = data.terraform_remote_state.cluster.outputs.cluster_ca
    token                  = data.aws_eks_cluster_auth.this.token
  }
}
```

Helm チャートの共通デプロイパターンをモジュール化する際は、chart のバージョンと values を変数化し、環境ごと(dev/stg/prod)の tfvars で差分だけを吸収する形にすると、チャート更新時の変更箇所が最小限になります。

```hcl
module "monitoring_stack" {
  source       = "./modules/platform/monitoring"
  chart_version = var.prometheus_chart_version
  values_override = var.prometheus_values_override
  namespace    = "monitoring"
}
```

## クラウド別の関係性

- **AWS**: EKS クラスタでは IAM Roles for Service Accounts(IRSA)や、より新しい EKS Pod Identity を Helm チャートの ServiceAccount アノテーションと連携させるパターンが一般的です。`aws_iam_role` の ARN を `helm_release` の `set` ブロックや `values` に渡し、Pod からの AWS API アクセスを制御します。
- **GCP**: GKE では Workload Identity を使い、Kubernetes ServiceAccount と Google Service Account を紐付けます。`google_service_account_iam_member` リソースと `kubernetes_service_account` の annotation(`iam.gke.io/gcp-service-account`)を組み合わせるのが定番です。
- **Azure**: AKS では Azure AD Workload Identity や、CSI ドライバ経由での Key Vault 連携が Helm チャートの values としてよく登場します。`azurerm_user_assigned_identity` の client ID を helm values に渡す構成です。

いずれのクラウドでも、クラウド側の IAM/認証リソースと Kubernetes 側の ServiceAccount・Helm values を同一 Terraform 構成内で紐付けられる点が、Terraform でこのレイヤーまで統合管理する大きな利点です。

## 注意点

1. **1 apply 方式のリスク**: クラスタ作成と kubernetes/helm リソースのデプロイを同一 state・同一 apply で行うと、初回作成時に kubernetes provider がまだ存在しないクラスタへの接続を試みてエラーになることがあります。`depends_on` を丁寧に設定しても provider の設定自体は apply 前に評価されるため根本解決にはならず、cluster と platform を state 分離するのが安全です。
2. **helm_release のタイムアウトと atomic**: `helm_release` には `timeout` と `atomic` 引数があり、`atomic = true` にするとデプロイ失敗時に自動ロールバックされますが、Terraform 側の apply は失敗として扱われるため、CI のリトライ設計と合わせて検討する必要があります。
3. **CRD の削除順序**: Helm チャートで CRD をインストールしている場合、`helm_release` を destroy しても CRD 自体は残ることがあり(Helm の仕様)、依存するカスタムリソースが残存した状態で namespace 削除がハングすることがあります。destroy の順序と `kubectl` での後始末手順をドキュメント化しておくべきです。
4. **ドリフト検知**: `kubectl apply` や `helm upgrade` を手動実行すると Terraform state との乖離が発生します。運用ルールとして「Kubernetes リソースへの変更は必ず Terraform 経由」を徹底し、可能であれば OPA/Kyverno などのポリシーで手動変更を制限することも検討してください。
5. **values の機密情報**: `helm_release` の `values` や `set` に平文でパスワードや API キーを書かない。`set_sensitive` を使うか、External Secrets Operator や Vault と連携して Kubernetes Secret 側で注入する設計にする方が安全です。

## FAQ

**Q1. kubernetes_manifest と kubectl_manifest(kubectl provider)はどちらを使うべきですか?**

`kubernetes_manifest`(hashicorp/kubernetes provider)は公式サポートですが、CRD が存在しない段階での plan に弱く、また一部の CRD で型変換エラーが起きることがあります。サードパーティの `kubectl_manifest`(gavinbunney/kubectl provider)は柔軟性が高くこの問題を回避しやすい一方、メンテナンス状況に依存するリスクがあります。公式サポートを優先しつつ、CRD 絡みで問題が出た場合の代替手段として `kubectl_manifest` を検討する、という位置づけが実務的です。

**Q2. Helm チャートのアップグレードで意図しないダウンタイムが発生しないか不安です。どう対策しますか?**

`helm_release` に `values` の diff がある場合、Terraform は plan 時点で変更を検知しますが、実際にどの Pod がどう再起動されるかまでは表示されません。事前に `helm diff upgrade`(Helm Diff プラグイン)や、ステージング環境での適用確認を CI に組み込むこと、また `helm_release` の `wait = true` と `timeout` を適切に設定してロールアウトの完了を待つことが有効です。クリティカルなワークロードでは Blue/Green や Canary の仕組みを別途 Argo Rollouts などで用意する構成も検討してください。

**Q3. マルチクラスタ環境で kubernetes/helm provider の設定をどう管理すればスケールしますか?**

provider ブロックはリソースのように `for_each` でループできないという制約があるため、クラスタごとにモジュールを分けて呼び出し、各モジュール内で provider を設定するパターンが一般的です。あるいは Terraform 1.9 以降の `provider` の `alias` を活用し、少数の固定クラスタであれば alias 付き provider を明示的に複数定義する方法もあります。クラスタ数が多く動的に増減する場合は、Terragrunt や Terraform Cloud のワークスペース分割など、モジュール外のオーケストレーション層でクラスタごとの実行単位を分ける設計の方が現実的です。

## まとめ

kubernetes provider と helm provider を組み合わせることで、クラウドインフラからアプリケーション基盤までを Terraform 上で一貫して管理できますが、state の分離設計と provider 依存関係の扱いを誤ると、apply の失敗やドリフトといった運用上のトラブルにつながりやすい領域でもあります。クラスタ層とプラットフォーム層を state レベルで分離し、モジュール化によって環境差分を最小化する設計を基本方針としつつ、GitOps ツールとの役割分担も含めて、自分たちのチームに合った運用ルールを早い段階で明文化しておくことが、長期的な保守性につながります。
