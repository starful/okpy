import os

# ============================================================
#  OKPy — technical blog
# ============================================================

SITE_CONFIG = {
    "project_name": "okpy",
    "site_name": "OKPy",
    "site_url": os.getenv("SITE_URL", "https://okpy.net"),
    "tagline": "Python · Cloud · Terraform · Data Analysis · PM",
    "site_mode": "blog",
    "gcs_image_base": os.getenv(
        "GCS_IMAGE_BASE",
        "https://storage.googleapis.com/ok-project-assets/okpy",
    ),

    "ga_id": os.getenv("GA_ID", "G-L7ZTNPYEF6"),
    "adsense_client_id": os.getenv(
        "ADSENSE_CLIENT_ID", "ca-pub-8780435268193938"
    ),
    "default_lang": "ja",

    "emoji": "🐍",
  "accent_color": "#4a4540",
  "bg_dot_color": "#c9c0b4",

    "blog_categories": {
        "python": {
            "label": "Python",
            "emoji": "🐍",
            "hub_suffix": "ライブラリ",
            "description": "NumPy, FastAPI, LangChain など。インストールから実践サンプルまで。",
        },
        "cloud": {
            "label": "Cloud",
            "emoji": "☁️",
            "hub_suffix": "比較",
            "description": "AWS / GCP / Azure の同カテゴリサービスを表形式で比較。",
        },
        "terraform": {
            "label": "Terraform",
            "emoji": "🏗️",
            "hub_suffix": "IaC",
            "description": "Terraform / OpenTofu によるインフラコード化、モジュール、state 管理。",
        },
        "dev-method": {
            "label": "開発方法論",
            "emoji": "📐",
            "hub_suffix": "",
            "description": "ウォーターフォール、DevOps、TDD、サーバーレスなど開発手法の解説。",
        },
        "data-model": {
            "label": "Data Model",
            "emoji": "🗄️",
            "hub_suffix": "",
            "description": "概念・論理・物理データモデル、ERD、NoSQL、データガバナンス。",
        },
        "data-analysis": {
            "label": "Data Analysis",
            "emoji": "📊",
            "hub_suffix": "",
            "description": "効果サイズ、A/Bテスト、計測・実験設計。ベンチマークと方法論。",
        },
        "pmbok": {
            "label": "PMBOK",
            "emoji": "📋",
            "hub_suffix": "",
            "description": "PMBOK第7版、10の知識エリア、プロジェクトマネジメント実践。",
        },
        "agile-scrum": {
            "label": "Agile & Scrum",
            "emoji": "🔄",
            "hub_suffix": "",
            "description": "スクラム、アジャイル、スプリント、カンバン、PO/SMの役割。",
        },
        "fit-journey": {
            "label": "Fit Journey",
            "emoji": "🚀",
            "hub_suffix": "",
            "description": "CPF・PMF・SPF・GTM — スタートアップの成長ロードマップ。",
        },
    },

    "footer_tagline": "Python, cloud, Terraform, data analysis, and software engineering practices.",
    "footer_year": "2026",
}
