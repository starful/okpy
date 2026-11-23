---
title: 'Terraform で実現する Azure Landing Zone:エンタープライズスケールアーキテクチャの実践'
date: 2026-11-23
category: terraform
slug: terraform-azure-landing-zones-implementing-microsoft-s-enterprise-scale-architec
summary: 'Azure 上で複数チーム・複数サブスクリプションを統制しながらシステムを展開する場合、Microsoft が提唱する「Azure Landing Zone(エンタープライズスケールアーキテクチャ)」が事実上の標準設計となっています。本記事では、この設計思想を Terraform でどう実装するかを、概念・HCL…'
cover: 'https://storage.googleapis.com/ok-project-assets/okpy/20261123193945.jpg'
lang: ja
---

# Terraform で実現する Azure Landing Zone:エンタープライズスケールアーキテクチャの実践

![cover](https://storage.googleapis.com/ok-project-assets/okpy/20261123193945.jpg)


Azure 上で複数チーム・複数サブスクリプションを統制しながらシステムを展開する場合、Microsoft が提唱する「Azure Landing Zone(エンタープライズスケールアーキテクチャ)」が事実上の標準設計となっています。本記事では、この設計思想を Terraform でどう実装するかを、概念・HCL 例・state 管理・モジュール構成・注意点・FAQ の順に解説します。

## Azure Landing Zone とは何か

Azure Landing Zone は、単一のサブスクリプションにすべてのリソースを詰め込むのではなく、「管理グループ(Management Group)」という階層構造の下にサブスクリプションを分離し、用途ごとにガバナンスを適用する設計パターンです。代表的な分類は以下の通りです。

- **Platform 系**:Management、Connectivity、Identity といった全社共通基盤を担うサブスクリプション群
- **Landing Zone 系**:実際にアプリケーションがデプロイされる「Corp」「Online」などのサブスクリプション群
- **Sandbox / Decommissioned**:検証用、廃止予定リソースの隔離先

これらは Azure Policy、RBAC、ネットワークトポロジ(Hub & Spoke)と組み合わさって初めて機能します。Terraform で扱う対象は、この管理グループ階層、ポリシー割り当て、サブスクリプションのエイリアス管理、そして Hub & Spoke の接続性です。

AWS でいう Organizations + Control Tower、GCP でいう Resource Manager の Organization/Folder 階層に相当する概念だと捉えると理解が早くなります。いずれのクラウドも「組織階層でガバナンスを適用し、個々のワークロードは疎結合なサブアカウント/プロジェクトに展開する」という発想は共通しています。Terraform を使えば、この三者のコード化アプローチをほぼ同じ心構え(階層ごとに state を分離し、ポリシーをコードでバージョン管理する)で扱えるのが大きな利点です。

## 管理グループ階層を Terraform で定義する

まずは管理グループの階層そのものを HCL で表現します。`azurerm` プロバイダーの `azurerm_management_group` リソースを使います。

```hcl
resource "azurerm_management_group" "root" {
  display_name = "Contoso"
}

resource "azurerm_management_group" "platform" {
  display_name               = "Platform"
  parent_management_group_id = azurerm_management_group.root.id
}

resource "azurerm_management_group" "landing_zones" {
  display_name               = "LandingZones"
  parent_management_group_id = azurerm_management_group.root.id
}

resource "azurerm_management_group" "corp" {
  display_name               = "Corp"
  parent_management_group_id = azurerm_management_group.landing_zones.id
}

resource "azurerm_management_group" "online" {
  display_name               = "Online"
  parent_management_group_id = azurerm_management_group.landing_zones.id
}
```

この階層が整ったら、サブスクリプションを各管理グループに関連付けます。

```hcl
resource "azurerm_management_group_subscription_association" "corp_sub" {
  management_group_id = azurerm_management_group.corp.id
  subscription_id      = "/subscriptions/${var.corp_subscription_id}"
}
```

## ポリシーの割り当て

ガバナンスの中核はポリシーです。Landing Zone に対しては「許可されたリージョンのみデプロイ可」「タグ必須」「特定 SKU の禁止」などを強制します。

```hcl
resource "azurerm_management_group_policy_assignment" "allowed_locations" {
  name                 = "allowed-locations"
  management_group_id = azurerm_management_group.landing_zones.id
  policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c"

  parameters = jsonencode({
    listOfAllowedLocations = {
      value = ["japaneast", "japanwest"]
    }
  })
}
```

ポリシー定義 ID は Microsoft が提供するビルトインポリシーのセットから選択することがほとんどで、独自定義も `azurerm_policy_definition` で作成できます。

## Hub & Spoke ネットワークの実装

Connectivity サブスクリプションには Hub 仮想ネットワークを配置し、各 Landing Zone の Spoke VNet とピアリングします。

```hcl
resource "azurerm_virtual_network" "hub" {
  name                = "vnet-hub"
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.connectivity.name
}

resource "azurerm_virtual_network" "spoke_corp" {
  name                = "vnet-spoke-corp"
  address_space       = ["10.1.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.corp.name
}

resource "azurerm_virtual_network_peering" "hub_to_spoke" {
  name                      = "hub-to-corp"
  resource_group_name      = azurerm_resource_group.connectivity.name
  virtual_network_name     = azurerm_virtual_network.hub.name
  remote_virtual_network_id = azurerm_virtual_network.spoke_corp.id
  allow_forwarded_traffic   = true
}

resource "azurerm_virtual_network_peering" "spoke_to_hub" {
  name                      = "corp-to-hub"
  resource_group_name      = azurerm_resource_group.corp.name
  virtual_network_name     = azurerm_virtual_network.spoke_corp.name
  remote_virtual_network_id = azurerm_virtual_network.hub.id
  allow_forwarded_traffic   = true
}
```

AWS の Transit Gateway による VPC 相互接続、GCP の Shared VPC による共有ネットワークと機能的にはほぼ等価です。ただし Azure はピアリングが双方向定義必須である点が AWS/GCP と異なるため、モジュール化する際は両方向のリソースを必ずセットで生成するようにしてください。

## state 管理の設計

Landing Zone 規模の構成では、単一の state ファイルにすべてを詰め込むと以下の問題が発生します。

- apply のたびに無関係なサブスクリプションまでロックされる
- plan の実行時間が肥大化する
- 誤ったリソース削除の影響範囲が全社規模になる

そのため、階層・ドメインごとに state を分割するのが定石です。

```
state/
├── platform/management-groups/   # 管理グループとポリシー
├── platform/connectivity/        # Hub VNet, Firewall, DNS
├── platform/identity/            # Entra ID 連携、PIM
├── landingzone/corp/             # Corp サブスクリプション単位
└── landingzone/online/
```

バックエンドには Azure Storage Account を使うのが一般的です。

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "sttfstateprod"
    container_name        = "tfstate"
    key                    = "platform/connectivity.tfstate"
  }
}
```

サブスクリプション間で state を分けることで、`terraform_remote_state` データソースを使い、Connectivity の Hub VNet ID を Landing Zone 側から参照できます。

```hcl
data "terraform_remote_state" "connectivity" {
  backend = "azurerm"
  config = {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "sttfstateprod"
    container_name        = "tfstate"
    key                    = "platform/connectivity.tfstate"
  }
}
```

AWS の S3 + DynamoDB ロックによる state 分離、GCP の GCS backend による同様の構成と設計思想は共通していますが、Azure Storage Account のリース機構によるロックは追加のロックテーブルが不要な点がシンプルです。

## モジュール構成のベストプラクティス

Microsoft は公式に `Azure/terraform-azurerm-avm-ptn-alz` のような Azure Verified Module(AVM)群を提供しています。これらをベースに、自組織用のラッパーモジュールを作るのが現実的なアプローチです。

```
modules/
├── management-groups/
├── policy-assignments/
├── hub-network/
└── landing-zone-subscription/
    ├── main.tf       # RG, VNet, NSG, ピアリングを一式生成
    ├── variables.tf
    └── outputs.tf
```

Landing Zone モジュールを呼び出す側は、サブスクリプションごとにディレクトリを分け、差分は変数で吸収します。

```hcl
module "landing_zone_corp" {
  source               = "../../modules/landing-zone-subscription"
  subscription_id       = var.corp_subscription_id
  management_group_id = azurerm_management_group.corp.id
  hub_vnet_id           = data.terraform_remote_state.connectivity.outputs.hub_vnet_id
  address_space         = ["10.1.0.0/16"]
}
```

この構成により、新しい Landing Zone(新規サブスクリプション)を追加する作業は「ディレクトリをコピーして変数を書き換える」だけに単純化できます。

## 注意点

- **サブスクリプションの作成は Terraform だけでは完結しない**ケースが多く、`azurerm_subscription` でエイリアスから作成できますが、課金アカウントの権限設計によっては事前に Enrollment Account や Billing Scope の準備が必要です。
- **ポリシーの `DeployIfNotExists` や `Modify` 効果を持つ割り当て**は、Terraform apply 後に Azure 側でコンプライアンス評価が非同期に走るため、apply 直後の `plan` で差分が出ているように見えることがあります。焦らず評価完了を待ってから再確認してください。
- **管理グループの削除は子要素が残っていると失敗**します。Terraform でもこの依存関係を正しく表現しないと destroy 時にエラーになるため、`depends_on` を明示するか、階層の末端から順にリソースを定義してください。
- **RBAC のロールアサインメントは管理グループレベルで継承される**ため、意図せず広い範囲に権限を付与してしまうリスクがあります。最小権限の原則を徹底し、Landing Zone 単位の割り当てはなるべく個別サブスクリプションで行いましょう。

## FAQ

**Q1. Landing Zone の state は本当に全部分割すべきですか?小規模組織でも必要ですか?**
小規模でサブスクリプションが数個程度であれば、Platform 層とLanding Zone 層の2分割程度でも十分機能します。重要なのは「変更頻度が異なるもの」「影響範囲が異なるもの」を同じ state に混在させないことです。組織の成長に合わせて段階的に分割すればよく、最初から過剰に細分化する必要はありません。

**Q2. AVM(Azure Verified Modules)を使うべきか、自前でモジュールを書くべきか?**
エンタープライズスケールアーキテクチャの標準パターンに忠実に従うなら AVM の `alz` 系モジュールを基盤にするのが効率的です。ただし社内の命名規則やタグ付けポリシーが独自である場合、AVM をラップする薄いモジュール層を自前で用意し、差分を吸収する設計にすると保守性が上がります。

**Q3. マルチクラウド環境で AWS や GCP の Landing Zone と Azure Landing Zone を統一的に管理できますか?**
Terraform 自体はクラウド非依存なので、同じ CI/CD パイプラインや state 管理の作法(階層分割、リモートバックエンド、モジュール化)を各クラウドに適用できます。ただし Management Group・Organization・Resource Manager の階層モデルやポリシーエンジンの挙動はクラウドごとに異なるため、抽象化レイヤーを作るよりも、各クラウド向けに専用モジュール群を用意し、運用プロセス(命名規則、タグ戦略、CI 構成)だけを共通化する方が現実的です。

## まとめ

Azure Landing Zone の Terraform 実装は、単なるリソース定義ではなく「管理グループ階層」「ポリシー」「ネットワークトポロジ」「state 分割」「モジュール設計」を一体として扱うガバナンス基盤の構築です。AWS・GCP の類似概念と発想を比較しながら設計すると、マルチクラウド組織でも一貫した統治モデルを維持しやすくなります。まずは Platform 層を固め、そこから Landing Zone モジュールを量産できる体制を整えることが、長期的な運用負荷を下げる最短ルートです。
