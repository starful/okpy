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


def detect_category(tags: list, title: str = "") -> str:
    tag_set = {t.strip() for t in tags if t}

    for hatena_tag, category in HATENA_TAG_PRIORITY:
        if hatena_tag in tag_set:
            return category

    if any(t.lower() in CLOUD_TAGS for t in tag_set):
        return "cloud"
    if any(k in (title or "") for k in CLOUD_TITLE_KEYWORDS):
        return "cloud"

    return "python"
