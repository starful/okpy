"""Hatena tag → okpy category mapping (shared by app and export scripts)."""

# Higher priority first when multiple Hatena tags match.
HATENA_TAG_PRIORITY = [
    ("Fit Journey", "fit-journey"),
    ("Agile&Scrum", "agile-scrum"),
    ("PMBOK", "pmbok"),
    ("Data Model", "data-model"),
    ("開発方法論", "dev-method"),
]

CLOUD_TAGS = {"aws", "gcp", "azure", "cloud"}
CLOUD_TITLE_KEYWORDS = ("AWS", "GCP", "Azure", "クラウド")
TERRAFORM_TAGS = {"terraform", "opentofu", "iac"}
TERRAFORM_TITLE_KEYWORDS = ("Terraform", "OpenTofu", "IaC")

# Known okpy categories that must never be collapsed into python.
PRESERVE_CATEGORIES = frozenset(
    {
        "python",
        "cloud",
        "terraform",
        "dev-method",
        "data-model",
        "pmbok",
        "agile-scrum",
        "fit-journey",
    }
)


def detect_category(tags: list, title: str = "", *, current: str | None = None) -> str:
    """Map Hatena tags / title hints to an okpy category.

    Existing archive categories are preserved when `current` is already set.
    Does not force unrelated topics into python.
    """
    cur = (current or "").strip().lower()
    if cur in PRESERVE_CATEGORIES and cur not in ("python",):
        return cur

    tag_set = {t.strip() for t in tags if t}

    for hatena_tag, category in HATENA_TAG_PRIORITY:
        if hatena_tag in tag_set:
            return category

    if any(t.lower() in TERRAFORM_TAGS for t in tag_set):
        return "terraform"
    if any(k in (title or "") for k in TERRAFORM_TITLE_KEYWORDS):
        return "terraform"

    if any(t.lower() in CLOUD_TAGS for t in tag_set):
        return "cloud"
    if any(k in (title or "") for k in CLOUD_TITLE_KEYWORDS):
        return "cloud"

    if cur == "python" or any(t.lower() == "python" for t in tag_set):
        return "python"

    # Unknown — keep current if valid, else leave unclassified as python only for new exports
    if cur in PRESERVE_CATEGORIES:
        return cur
    return "python"
