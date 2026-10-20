---
title: 'Terraform による AKS クラスター構築とノードプール自動スケーリングのベストプラクティス'
date: 2026-10-20
category: terraform
slug: terraform-aks-cluster-provisioning-and-node-pool-autoscaling-best-practices
summary: 'Azure Kubernetes Service（AKS）は、マネージドな Kubernetes コントロールプレーンを提供する Azure のサービスです。Terraform を使って AKS クラスターを構築することで、インフラをコードとして管理し、再現性のあるデプロイを実現できます。本記事では、AKS クラ…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261020151125.jpg'
lang: ja
---

# Terraform による AKS クラスター構築とノードプール自動スケーリングのベストプラクティス

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261020151125.jpg)


## はじめに

Azure Kubernetes Service（AKS）は、マネージドな Kubernetes コントロールプレーンを提供する Azure のサービスです。Terraform を使って AKS クラスターを構築することで、インフラをコードとして管理し、再現性のあるデプロイを実現できます。本記事では、AKS クラスターの基本構成、ノードプールのオートスケーリング設定、Terraform state の扱い方、モジュール化の手法、運用上の注意点について解説します。

## AKS と Terraform の基本概念

AKS は Azure 上でコントロールプレーンを Azure が管理し、ユーザーはワーカーノード（ノードプール）のみを管理するモデルを取ります。Terraform の `azurerm` プロバイダーを使うことで、クラスター本体、ノードプール、ネットワーク、IAM（Azure AD 統合）などをコードで一元管理できます。

主要なリソースは以下の通りです。

- `azurerm_kubernetes_cluster`: AKS クラスター本体（デフォルトノードプールを含む）
- `azurerm_kubernetes_cluster_node_pool`: 追加のノードプール
- `azurerm_resource_group`: リソースグループ
- `azurerm_virtual_network` / `azurerm_subnet`: ネットワーク基盤

AKS のオートスケーリングには主に2種類あります。

1. **Cluster Autoscaler**: ノード数を Pod のスケジューリング要求に応じて増減させる
2. **Horizontal Pod Autoscaler (HPA)**: Pod のレプリカ数を CPU/メモリ使用率などに応じて増減させる

本記事では主に Cluster Autoscaler を Terraform でどう設定するかに焦点を当てます。

## 基本的な HCL 例

まずはシンプルな AKS クラスターの定義例を示します。

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
  }
  required_version = ">= 1.5.0"
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "aks" {
  name     = "rg-aks-prod"
  location = "japaneast"
}

resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-prod-cluster"
  location            = azurerm_resource_group.aks.location
  resource_group_name = azurerm_resource_group.aks.name
  dns_prefix          = "aksprod"
  kubernetes_version  = "1.29.2"

  default_node_pool {
    name                = "system"
    vm_size             = "Standard_D4s_v5"
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 5
    os_disk_size_gb      = 64
    vnet_subnet_id       = azurerm_subnet.aks.id
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
  }

  tags = {
    environment = "production"
    managed_by  = "terraform"
  }
}
```

ここで重要なのは `enable_auto_scaling = true` と `min_count` / `max_count` の組み合わせです。これにより Cluster Autoscaler が有効化され、ノードプール内のノード数が負荷に応じて自動的に増減します。

### 追加ノードプール（ワークロード専用）

システムノードプールとは別に、アプリケーション用のノードプールを分離するのが一般的なベストプラクティスです。

```hcl
resource "azurerm_kubernetes_cluster_node_pool" "workload" {
  name                  = "workload"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = "Standard_D8s_v5"
  enable_auto_scaling   = true
  min_count             = 3
  max_count             = 10
  mode                  = "User"
  vnet_subnet_id        = azurerm_subnet.aks.id

  node_labels = {
    "workload-type" = "application"
  }

  node_taints = [
    "workload=application:NoSchedule"
  ]

  tags = {
    environment = "production"
  }
}
```

`mode = "User"` を指定することで、システム系ワークロードとアプリケーションワークロードを分離できます。`node_taints` と `node_labels` を組み合わせることで、特定の Pod のみをこのノードプールにスケジューリングさせる制御も可能です。

### スポット VM を使ったコスト最適化ノードプール

バッチ処理や耐障害性のあるワークロード向けに、スポット VM ノードプールを構成することでコストを大幅に削減できます。

```hcl
resource "azurerm_kubernetes_cluster_node_pool" "spot" {
  name                  = "spot"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = "Standard_D4s_v5"
  priority              = "Spot"
  eviction_policy       = "Delete"
  spot_max_price        = -1
  enable_auto_scaling   = true
  min_count             = 0
  max_count             = 20
  mode                  = "User"

  node_labels = {
    "kubernetes.azure.com/scalesetpriority" = "spot"
  }

  node_taints = [
    "kubernetes.azure.com/scalesetpriority=spot:NoSchedule"
  ]
}
```

`min_count = 0` を許容することで、不要なときはスポットノードを完全にゼロへスケールダウンできます。

## Cluster Autoscaler の詳細設定

AKS の Cluster Autoscaler は `azurerm_kubernetes_cluster` のトップレベルで細かいチューニングも可能です。

```hcl
resource "azurerm_kubernetes_cluster" "main" {
  # ... 省略

  default_node_pool {
    name                = "system"
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 5
  }

  auto_scaler_profile {
    balance_similar_node_groups      = true
    expander                         = "least-waste"
    max_graceful_termination_sec     = "600"
    scale_down_delay_after_add       = "10m"
    scale_down_unneeded              = "10m"
    scale_down_utilization_threshold = "0.5"
  }
}
```

`auto_scaler_profile` ブロックにより、スケールダウンの挙動を細かく制御できます。`scale_down_unneeded` はノードが「不要」と判断されてから実際に削除されるまでの待機時間で、頻繁なスケールの振動（フラッピング）を防ぐために重要なパラメータです。

## Terraform State の扱い方

AKS のような長期運用されるインフラでは、state の管理方法が運用の安定性を大きく左右します。

### リモート state の利用

ローカル state はチーム開発では危険です。Azure Storage Account をバックエンドとしたリモート state を必ず使用してください。

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "tfstateaksprod"
    container_name       = "tfstate"
    key                  = "aks-prod.tfstate"
  }
}
```

state ファイルにはクレデンシャルに近い情報（kubeconfig の一部やサービスプリンシパルの参照など）が含まれる可能性があるため、Storage Account には必ず暗号化とアクセス制限（Private Endpoint、RBAC）を設定してください。

### state ロックと同時実行制御

`azurerm` バックエンドは Blob Lease を利用した state ロックを自動的に行います。CI/CD パイプラインから `terraform apply` を実行する場合は、同時実行を避けるためにパイプライン側でも排他制御（concurrency group など）を設定することを推奨します。

### ノードプールの再作成に関する注意

`vm_size`、`vnet_subnet_id`、`os_disk_size_gb` など一部の属性を変更すると、Terraform はノードプールを **破棄して再作成** します（`default_node_pool` は特に注意が必要で、多くの属性変更がクラスター全体の再作成を引き起こします）。本番環境では、変更前に必ず `terraform plan` の出力を確認し、`-replace` や `create_before_destroy` の挙動を理解した上で適用してください。

```hcl
resource "azurerm_kubernetes_cluster_node_pool" "workload" {
  # ...
  lifecycle {
    create_before_destroy = true
    ignore_changes        = [node_count]
  }
}
```

`enable_auto_scaling = true` の場合、Cluster Autoscaler が実際のノード数を動的に変更するため、`node_count` を Terraform の管理対象外にする（`ignore_changes` に含める）のが定石です。これを忘れると、Terraform が desired state と実際のノード数の差分を「ドリフト」として検知し、意図しないスケールダウンを引き起こすことがあります。

## モジュール化の設計

複数環境（dev/stg/prod）や複数クラスターを運用する場合、モジュール化は不可欠です。

```
modules/
  aks-cluster/
    main.tf
    variables.tf
    outputs.tf
environments/
  prod/
    main.tf
    terraform.tfvars
  dev/
    main.tf
    terraform.tfvars
```

モジュール側（`modules/aks-cluster/variables.tf`）の例です。

```hcl
variable "cluster_name" {
  type = string
}

variable "node_pools" {
  type = map(object({
    vm_size    = string
    min_count  = number
    max_count  = number
    mode       = string
    priority   = optional(string, "Regular")
  }))
}
```

呼び出し側（`environments/prod/main.tf`）では以下のようにシンプルに利用できます。

```hcl
module "aks" {
  source       = "../../modules/aks-cluster"
  cluster_name = "aks-prod-cluster"

  node_pools = {
    workload = {
      vm_size   = "Standard_D8s_v5"
      min_count = 3
      max_count = 10
      mode      = "User"
    }
    spot = {
      vm_size   = "Standard_D4s_v5"
      min_count = 0
      max_count = 20
      mode      = "User"
      priority  = "Spot"
    }
  }
}
```

モジュール内で `for_each` を使ってノードプールを動的に生成することで、環境ごとに tfvars だけを変えてスケール構成を変更できる柔軟な構造になります。

```hcl
resource "azurerm_kubernetes_cluster_node_pool" "pools" {
  for_each              = var.node_pools
  name                  = each.key
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = each.value.vm_size
  enable_auto_scaling   = true
  min_count             = each.value.min_count
  max_count             = each.value.max_count
  mode                  = each.value.mode
  priority              = each.value.priority

  lifecycle {
    ignore_changes = [node_count]
  }
}
```

## 他クラウドとの関係

AKS は Azure 固有のサービスですが、Cluster Autoscaler の概念自体は他クラウドの Kubernetes サービスと共通しています。

- **AWS**: EKS では `aws_eks_node_group` に `scaling_config` を設定し、Cluster Autoscaler または Karpenter と組み合わせて使うのが一般的です。ノードプールの思想は AKS とほぼ同じですが、AWS では Auto Scaling Group（ASG）がベースになっている点が異なります。
- **GCP**: GKE では `google_container_node_pool` の `autoscaling` ブロックで `min_node_count` / `max_node_count` を指定します。GKE Autopilot モードを使うとノードプール管理自体を Google に委任できる点が AKS との大きな違いです。
- **Azure**: AKS では Virtual Machine Scale Sets（VMSS）がノードプールの実体であり、Terraform の `enable_auto_scaling` はこの VMSS のスケーリング設定を制御しています。

複数クラウドで同様の構成を取りたい場合、Terraform モジュールの抽象化レイヤーを揃えておくことで、クラウド間の移行やマルチクラウド運用の設計コストを下げられます。

## 運用上の注意点

- **ノードプールの最小数はゼロにしない（システムプールの場合）**: `mode = "System"` のノードプールは最低でも 1〜2 ノードを維持する必要があります。コントロールプレーンの監視コンポーネントが動作し続けるためです。スポットやワークロード専用プールは `min_count = 0` でも問題ありません。
- **Pod Disruption Budget (PDB) の設定**: Cluster Autoscaler がノードをスケールダウンする際、PDB が適切に設定されていないとアプリケーションの可用性が損なわれる可能性があります。
- **リソースリクエスト/リミットの明示**: Cluster Autoscaler は Pod の `requests` を基準にスケジューリング可能性を判断するため、リクエストが未設定だと正しくスケールしません。
- **kubernetes_version のアップグレード**: Terraform で `kubernetes_version` を変更するとローリングアップグレードが開始されます。本番環境では事前にステージング環境で検証し、`max_surge` の設定も確認してください。
- **Azure AD RBAC との統合**: `azure_active_directory_role_based_access_control` ブロックを使い、kubeconfig の資格情報管理を Azure AD に委任することで、クレデンシャル漏洩のリスクを低減できます。
- **Terraform と kubectl の責務分離**: Terraform はクラスターとノードプールのインフラ管理に留め、Kubernetes マニフェスト（Deployment や Service）は Helm や Argo CD など別のツールで管理するのがベストプラクティスです。両者を混在させると state の肥大化や依存関係の複雑化を招きます。

## FAQ

**Q1. `enable_auto_scaling` を有効にすると `node_count` はどう扱うべきですか？**

A. `enable_auto_scaling = true` の場合、実際のノード数は Cluster Autoscaler が動的に制御するため、Terraform 側で `node_count` を明示的に管理すると適用のたびにドリフトが検出されます。`lifecycle { ignore_changes = [node_count] }` を設定し、Terraform にはこの属性を無視させるのが推奨される運用方法です。

**Q2. デフォルトノードプール（`default_node_pool`）の設定を変更すると、クラスター全体が再作成されますか？**

A. 一部の属性（`vm_size`、`vnet_subnet_id`、`zones` など）を変更すると、デフォルトノードプールの再作成が必要になり、場合によってはクラスター自体の再作成につながることがあります。本番運用では、デフォルトノードプールは最小限の役割（システムコンポーネント専用）に留め、アプリケーションワークロードは別の `azurerm_kubernetes_cluster_node_pool` リソースで管理することで、変更時の影響範囲を小さく保てます。

**Q3. 複数のノードプールでオートスケーリングの挙動がばらつく場合、どう対処すればよいですか？**

A. `auto_scaler_profile` の `balance_similar_node_groups` を `true` に設定すると、似た構成のノードプール間でノード数のバランスを取るよう Cluster Autoscaler が動作します。また `expander` の設定（`least-waste`、`most-pods`、`priority` など）を適切に選ぶことで、どのノードプールを優先的にスケールアウトするかを制御できます。複数プールが絡む場合は、それぞれの `min_count` / `max_count` と taints/labels の整合性を定期的にレビューすることも重要です。

## まとめ

Terraform を用いた AKS クラスターの構築では、ノードプールの分離設計、Cluster Autoscaler の適切なチューニング、state の安全な管理、そしてモジュール化による環境間の一貫性確保が重要なポイントとなります。特に `ignore_changes` によるオートスケーリングとのドリフト回避、PDB やリソースリクエストの設定といった Kubernetes 側の前提条件も合わせて整えることで、安定した本番運用が実現できます。AWS の EKS や GCP の GKE とも設計思想は共通しており、マルチクラウド戦略を取る場合はこれらの対応関係を意識したモジュール設計が役立つでしょう。
