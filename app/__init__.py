from flask import Flask, jsonify, render_template, abort, redirect, request, Response, send_from_directory
from flask_compress import Compress
import csv
import json
import os
import re
import glob
import frontmatter
import markdown
import urllib.parse
from datetime import datetime

app = Flask(__name__)
Compress(app)

try:
    from .a8_affiliate import a8_banner_context
    from .amazon_affiliate import affiliate_context
    from .config import SITE_CONFIG
    from .home_data import (
        HOME_LIMIT,
        apply_card_covers,
        category_cover_pool,
        category_thumbnails,
        fallback_cover_for_post,
        popular_posts_from_gsc,
        posts_by_category,
    )
except ImportError:
    from a8_affiliate import a8_banner_context
    from amazon_affiliate import affiliate_context
    from config import SITE_CONFIG
    from home_data import (
        HOME_LIMIT,
        apply_card_covers,
        category_cover_pool,
        category_thumbnails,
        fallback_cover_for_post,
        popular_posts_from_gsc,
        posts_by_category,
    )

BASE_DIR = app.root_path
STATIC_DIR = os.path.join(BASE_DIR, "static")
POST_DIR = os.path.join(BASE_DIR, "content", "posts")
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
REDIRECTS_CSV = os.path.join(DATA_DIR, "redirects.csv")

CACHED_POSTS = []  # newest first
REDIRECT_MAP = {}  # path -> full new_url

# Hatena /archive/category/<name> → OKPy blog category
ARCHIVE_CATEGORY_MAP = {
    "python": "python",
    "lib": "python",
    "cloud": "cloud",
    "gcp": "cloud",
    "aws": "cloud",
    "azure": "cloud",
    "data model": "data-model",
    "data analysis": "data-analysis",
    "fit journey": "fit-journey",
    "agile&scrum": "agile-scrum",
    "開発方法論": "dev-method",
    "project position": "fit-journey",
    "エンジニアのコミュニケーション": "eng-comms",
    "AIモデル比較": "ai-models",
}


def _clean_md(text):
    text = re.sub(r"^```[a-z]*\n", "", text)
    text = re.sub(r"\n```$", "", text)
    if "---" in text and not text.startswith("---"):
        text = "---" + text.split("---", 1)[1]
    return text.strip()


_LIST_ITEM_RE = re.compile(r"^(\s*)([-*+]|\d+\.)\s")
_BLOCK_START_RE = re.compile(r"^(\s*)(#{1,6}\s|>|```|\|)")


def _normalize_markdown_lists(text):
    """Insert blank lines before list items so python-markdown renders <ul>/<ol>."""
    lines = text.splitlines()
    if not lines:
        return text

    out = []
    for i, line in enumerate(lines):
        if i > 0 and _LIST_ITEM_RE.match(line):
            prev = lines[i - 1]
            if prev.strip() and not _LIST_ITEM_RE.match(prev) and not _BLOCK_START_RE.match(prev):
                if out and out[-1].strip():
                    out.append("")
        out.append(line)
    return "\n".join(out)


def _wrap_code_blocks(html):
    def repl(match):
        pre = match.group(0)
        if "code-block" in pre:
            return pre
        return (
            '<div class="code-block">'
            '<button type="button" class="code-copy-btn" aria-label="コードをコピー">コピー</button>'
            f"{pre}</div>"
        )

    return re.sub(r"<pre\b[^>]*>.*?</pre>", repl, html, flags=re.DOTALL | re.IGNORECASE)


def _strip_duplicate_h1(body: str, title: str) -> str:
    """Remove leading H1 when it duplicates the article title (avoids empty TOC)."""
    lines = body.splitlines()
    if not lines or not lines[0].startswith("# "):
        return body
    h1 = lines[0][2:].strip()
    h1_plain = re.sub(r"[*_`]", "", h1)
    title_plain = re.sub(r"[*_`]", "", title).strip()
    if h1_plain == title_plain or title_plain in h1_plain or h1_plain in title_plain:
        return "\n".join(lines[1:]).lstrip()
    return body


def _first_image_in_markdown(body: str) -> str:
    match = re.search(r"!\[[^\]]*\]\(([^)]+)\)", body)
    return match.group(1).strip() if match else ""


def _public_image_url(url: str) -> str:
    """Map legacy local post images to the shared GCS bucket URL."""
    if not url:
        return ""
    url = url.strip()
    gcs_base = SITE_CONFIG.get(
        "gcs_image_base",
        "https://storage.googleapis.com/ok-project-assets/okpy",
    ).rstrip("/")
    local_prefixes = (
        "/static/images/posts/",
        "static/images/posts/",
    )
    for prefix in local_prefixes:
        if url.startswith(prefix):
            return f"{gcs_base}/{url[len(prefix):]}"
    return url


def _rewrite_local_post_images(text: str) -> str:
    if not text or "/static/images/posts/" not in text:
        return text
    gcs_base = SITE_CONFIG.get(
        "gcs_image_base",
        "https://storage.googleapis.com/ok-project-assets/okpy",
    ).rstrip("/")
    return text.replace("/static/images/posts/", f"{gcs_base}/")


def _resolve_article_cover(post, match, body: str) -> str:
    cover = str(post.get("cover") or match.get("cover") or "").strip()
    if not cover:
        cover = _first_image_in_markdown(body)
    return _public_image_url(cover)


_EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF]")


def _normalize_article_headings(body: str) -> str:
    """Promote deep Hatena-style headings (####/#####/######) to h2/h3."""
    out: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^(#{4,6})\s+(.+)$", line)
        if not match:
            out.append(line)
            continue
        level = len(match.group(1))
        text = match.group(2).strip()
        if level == 4 and "完全ガイド" in text and _EMOJI_RE.search(text):
            continue
        if level == 5 and _is_numbered_section(text):
            out.append(f"## {text}")
        elif level == 6:
            out.append(f"### {text}")
        elif level == 4 and _is_numbered_section(text):
            out.append(f"## {text}")
        else:
            out.append(line)
    return "\n".join(out)


def _toc_root_ul_inner(toc_html: str) -> str:
    start = toc_html.find('<div class="toc">')
    if start == -1:
        return ""
    ul_start = toc_html.find("<ul>", start)
    if ul_start == -1:
        return ""
    i = ul_start + 4
    depth = 1
    n = len(toc_html)
    while i < n and depth:
        if toc_html.startswith("<ul>", i):
            depth += 1
            i += 4
        elif toc_html.startswith("</ul>", i):
            depth -= 1
            i += 5
        else:
            i += 1
    return toc_html[ul_start + 4 : i - 5]


def _toc_top_level_items(ul_inner: str) -> list[str]:
    items: list[str] = []
    i, n = 0, len(ul_inner)
    while i < n:
        match = re.match(r"\s*<li>", ul_inner[i:])
        if not match:
            break
        i += match.end() - 4
        depth, start = 0, i
        while i < n:
            if ul_inner.startswith("<li>", i):
                depth += 1
                i += 4
            elif ul_inner.startswith("</li>", i):
                depth -= 1
                i += 5
                if depth == 0:
                    break
            else:
                i += 1
        items.append(ul_inner[start:i])
    return items


def _is_numbered_section(text: str) -> bool:
    text = text.strip()
    return bool(re.match(r"^\d+\.", text)) or bool(
        re.match(r"^(?:\S+\s+)+\d+\.\s", text)
    )


def _simplify_toc(toc_html: str) -> str:
    """Keep numbered section titles; flatten nested TOC when needed."""
    if not toc_html:
        return ""

    links = re.findall(r'<li><a href="([^"]+)">([^<]+)</a>', toc_html)
    numbered = [(href, text) for href, text in links if _is_numbered_section(text)]
    if numbered:
        items = "\n".join(
            f'<li><a href="{href}">{text}</a></li>' for href, text in numbered
        )
        return f'<div class="toc">\n<ul>\n{items}\n</ul>\n</div>'

    ul_inner = _toc_root_ul_inner(toc_html)
    if not ul_inner:
        return toc_html

    flat: list[str] = []
    for li in _toc_top_level_items(ul_inner):
        li_flat = re.sub(r"<ul>.*?</ul>", "", li, flags=re.DOTALL).strip()
        anchor = re.search(r"<a[^>]*>([^<]+)</a>", li_flat)
        if anchor:
            flat.append(li_flat)

    if not flat:
        return ""
    items = "\n".join(flat)
    return f'<div class="toc">\n<ul>\n{items}\n</ul>\n</div>'


def _toc_has_entries(toc_html: str) -> bool:
    if not toc_html:
        return False
    return bool(re.search(r"<li\b", toc_html))


def _absolute_url(path_or_url):
    if not path_or_url:
        return ""
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    return f"{SITE_CONFIG['site_url'].rstrip('/')}/{path_or_url.lstrip('/')}"


def load_redirects():
    global REDIRECT_MAP
    REDIRECT_MAP = {}
    if not os.path.isfile(REDIRECTS_CSV):
        return
    try:
        with open(REDIRECTS_CSV, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                old = (row.get("old_path") or row.get("old_url") or "").strip()
                new = (row.get("new_url") or row.get("new_path") or "").strip()
                if not old or not new:
                    continue
                if old.startswith("http"):
                    parsed = urllib.parse.urlparse(old)
                    old = parsed.path or "/"
                if not old.startswith("/"):
                    old = "/" + old
                REDIRECT_MAP[old] = new

        # Alias /entry/.../090000_1 → also accept /entry/.../090000 (Hatena variants)
        extras = {}
        for old, new in REDIRECT_MAP.items():
            m = re.match(r"^(/entry/\d{4}/\d{2}/\d{2}/\d{6})_\d+$", old)
            if m and m.group(1) not in REDIRECT_MAP:
                extras[m.group(1)] = new
        REDIRECT_MAP.update(extras)
        print(f"✅ Redirect rules loaded: {len(REDIRECT_MAP)}")
    except Exception as e:
        print(f"❌ Redirect load error: {e}")


def _legacy_archive_redirect(path: str):
    """Map Hatena archive URLs to home or a blog category."""
    prefix = "/archive/category/"
    if path.startswith(prefix):
        raw = path[len(prefix) :]
        name = urllib.parse.unquote(raw.split("/")[0]).strip()
        cat = ARCHIVE_CATEGORY_MAP.get(name.lower()) or ARCHIVE_CATEGORY_MAP.get(name)
        if cat and cat in SITE_CONFIG.get("blog_categories", {}):
            return redirect(f"/category/{cat}", code=301)
    return redirect("/", code=301)


def _strip_page_query_redirect():
    """Collapse Hatena ?page= soft-duplicates onto the clean path."""
    if "page" not in request.args:
        return None
    args = request.args.to_dict(flat=True)
    args.pop("page", None)
    path = request.path or "/"
    if args:
        return redirect(f"{path}?{urllib.parse.urlencode(args)}", code=301)
    return redirect(path, code=301)


def load_posts():
    global CACHED_POSTS
    posts = []
    if not os.path.isdir(POST_DIR):
        CACHED_POSTS = []
        return

    for fpath in glob.glob(os.path.join(POST_DIR, "**", "*.md"), recursive=True):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                raw = _clean_md(f.read())
            post = frontmatter.loads(raw)
            basename = os.path.basename(fpath).replace(".md", "")
            slug = str(post.get("slug") or basename).strip()
            category = str(post.get("category") or "python").strip().lower()
            if category not in SITE_CONFIG.get("blog_categories", {}):
                category = "python"
            cover = str(post.get("cover") or "").strip()
            if not cover:
                cover = _first_image_in_markdown(post.content or "")
            cover = _public_image_url(cover)
            posts.append(
                {
                    "slug": slug,
                    "title": str(post.get("title") or slug),
                    "summary": str(post.get("summary") or ""),
                    "date": str(post.get("date") or "2026-01-01"),
                    "category": category,
                    "cover": cover,
                    "lang": str(post.get("lang") or SITE_CONFIG.get("default_lang", "ja")),
                    "path": fpath,
                }
            )
        except Exception as e:
            print(f"⚠️ Skip post {fpath}: {e}")

    posts.sort(key=lambda x: x["date"], reverse=True)
    CACHED_POSTS = posts
    print(f"✅ Posts loaded: {len(CACHED_POSTS)}")


def _posts_for_category(category=None):
    if not category:
        return CACHED_POSTS
    return [p for p in CACHED_POSTS if p["category"] == category]


def _category_counts():
    cats = SITE_CONFIG.get("blog_categories", {})
    counts = {k: len(_posts_for_category(k)) for k in cats}
    counts["all"] = len(CACHED_POSTS)
    return counts


def _footer_ctx():
    cats = SITE_CONFIG.get("blog_categories", {})
    return {
        "site": SITE_CONFIG,
        "categories": cats,
        "category_counts": _category_counts(),
        "category_thumbnails": category_thumbnails(CACHED_POSTS, cats),
        "category_cover_pools": category_cover_pool(CACHED_POSTS, cats),
    }


@app.before_request
def apply_legacy_redirects():
    path = request.path

    # Dead Hatena surfaces → consolidate crawl budget
    if path == "/archive" or path.startswith("/archive/"):
        return _legacy_archive_redirect(path)
    if path == "/rss" or path.startswith("/rss/"):
        return redirect("/", code=301)

    if path in REDIRECT_MAP:
        return redirect(REDIRECT_MAP[path], code=301)
    if path != "/" and path.endswith("/"):
        trimmed = path.rstrip("/") or "/"
        if trimmed in REDIRECT_MAP:
            return redirect(REDIRECT_MAP[trimmed], code=301)
    if path != "/" and not path.endswith("/"):
        alt = path + "/"
        if alt in REDIRECT_MAP:
            return redirect(REDIRECT_MAP[alt], code=301)

    # Unmapped /entry/... (deleted or never imported) → home
    if path.startswith("/entry/"):
        return redirect("/", code=301)

    # /?page=TIMESTAMP soft-duplicates of the homepage (and other paths)
    page_redir = _strip_page_query_redirect()
    if page_redir is not None:
        return page_redir


load_redirects()
load_posts()


def _default_og_image():
    return _absolute_url("/static/images/logo.png")


@app.route("/")
def index():
    cats = SITE_CONFIG.get("blog_categories", {})
    ctx = _footer_ctx()
    pools = ctx["category_cover_pools"]
    by_cat = {
        key: apply_card_covers(posts, pools)
        for key, posts in posts_by_category(CACHED_POSTS, cats, HOME_LIMIT).items()
    }
    return render_template(
        "blog_index.html",
        latest_posts=apply_card_covers(CACHED_POSTS[:HOME_LIMIT], pools),
        popular_posts=apply_card_covers(
            popular_posts_from_gsc(CACHED_POSTS, REDIRECT_MAP, HOME_LIMIT), pools
        ),
        posts_by_category=by_cat,
        posts=apply_card_covers(CACHED_POSTS[:HOME_LIMIT], pools),
        active_category=None,
        canonical=SITE_CONFIG["site_url"].rstrip("/") + "/",
        og_image=_default_og_image(),
        **ctx,
    )


@app.route("/category/<category>")
def category_list(category):
    cats = SITE_CONFIG.get("blog_categories", {})
    if category not in cats:
        abort(404)
    ctx = _footer_ctx()
    canonical = f"{SITE_CONFIG['site_url'].rstrip('/')}/category/{category}"
    amazon = affiliate_context(category)
    a8 = a8_banner_context(category)
    thumb = (ctx.get("category_thumbnails") or {}).get(category) or ""
    og_image = _absolute_url(thumb) if thumb else _default_og_image()
    return render_template(
        "blog_index.html",
        posts=apply_card_covers(_posts_for_category(category), ctx["category_cover_pools"]),
        active_category=category,
        canonical=canonical,
        og_image=og_image,
        **amazon,
        **a8,
        **ctx,
    )


@app.route("/blog/<slug>")
def blog_post(slug):
    match = next((p for p in CACHED_POSTS if p["slug"] == slug), None)
    if not match:
        abort(404)

    with open(match["path"], "r", encoding="utf-8") as f:
        raw = _clean_md(f.read())
    post = frontmatter.loads(raw)
    body = _normalize_markdown_lists(post.content.replace("```markdown", "").strip())
    body = _rewrite_local_post_images(body)
    title = str(post.get("title") or slug)
    body = _strip_duplicate_h1(body, title)
    body = _normalize_article_headings(body)
    cover = _resolve_article_cover(post, match, body)
    if cover:
        body = re.sub(
            rf"!\[[^\]]*\]\({re.escape(cover)}\)\s*\n?",
            "",
            body,
            count=1,
        )
    cats = SITE_CONFIG.get("blog_categories", {})
    if not cover:
        cover = fallback_cover_for_post(
            match, category_cover_pool(CACHED_POSTS, cats)
        )
    md = markdown.Markdown(
        extensions=["tables", "toc", "fenced_code"],
        extension_configs={"toc": {"permalink": False, "toc_depth": 6}},
    )
    content_html = _wrap_code_blocks(md.convert(body))
    toc_html = _simplify_toc(md.toc) if _toc_has_entries(md.toc) else ""

    word_count = len(re.sub(r"<[^>]+>", "", body).split())
    read_minutes = max(1, round(word_count / 400))
    category = match["category"]
    cat_meta = SITE_CONFIG.get("blog_categories", {}).get(category, {})
    canonical = f"{SITE_CONFIG['site_url'].rstrip('/')}/blog/{slug}"
    cover_abs = _absolute_url(cover) if cover else ""
    amazon = affiliate_context(
        category, title=title, slug=slug, body=body
    )
    a8 = a8_banner_context(category)

    return render_template(
        "blog_post.html",
        title=title,
        content=content_html,
        toc=toc_html,
        read_minutes=read_minutes,
        post=post,
        cover=cover,
        cover_abs=cover_abs,
        slug=slug,
        category=category,
        category_label=cat_meta.get("label", category),
        category_emoji=cat_meta.get("emoji", ""),
        canonical=canonical,
        **amazon,
        **a8,
        **_footer_ctx(),
    )


@app.route("/guide")
@app.route("/guide/<path:_rest>")
def legacy_guide_redirect(_rest=None):
    return redirect("/", code=301)


@app.route("/item/<path:_rest>")
def legacy_item_redirect(_rest=None):
    return redirect("/", code=301)


@app.route("/robots.txt")
def robots_txt():
    base = SITE_CONFIG["site_url"].rstrip("/")
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )
    return Response(content, mimetype="text/plain")


@app.route("/ads.txt")
def ads_txt():
    return send_from_directory(STATIC_DIR, "ads.txt", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    base = SITE_CONFIG["site_url"].rstrip("/")
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [f"{base}/", f"{base}/guide/agentic-system"]
    for cat in SITE_CONFIG.get("blog_categories", {}):
        urls.append(f"{base}/category/{cat}")
    for p in CACHED_POSTS:
        urls.append(f"{base}/blog/{p['slug']}")

    nodes = []
    for i, loc in enumerate(urls):
        # Home + special guide slightly higher priority
        priority = "1.0" if i == 0 else ("0.9" if i == 1 else "0.8")
        nodes.append(
            f"<url><loc>{loc}</loc><lastmod>{today}</lastmod>"
            f"<changefreq>weekly</changefreq><priority>{priority}</priority></url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(nodes)
        + "</urlset>"
    )
    return Response(xml, mimetype="application/xml")


@app.route("/guide/agentic-system")
@app.route("/guide/agentic-system/")
def guide_agentic_system():
    """Interactive special: agentic AI system map (EN/JA/KO)."""
    return send_from_directory(
        os.path.join(STATIC_DIR, "guides"),
        "agentic-system.html",
        mimetype="text/html",
    )


@app.route("/about.html")
def about():
    return render_template("about.html", **_footer_ctx())


@app.route("/privacy.html")
def privacy():
    return render_template("privacy.html", site=SITE_CONFIG)


@app.route("/contact.html")
@app.route("/contact")
def contact():
    return render_template("contact.html", site=SITE_CONFIG)


@app.route("/favicon.ico")
@app.route("/favicon-32x32.png")
@app.route("/apple-touch-icon.png")
def serve_favicons():
    image_dir = os.path.join(STATIC_DIR, "images")
    filename = request.path.lstrip("/")
    local_path = os.path.join(image_dir, filename)
    if os.path.exists(local_path):
        return send_from_directory(image_dir, filename)
    abort(404)


@app.route("/site.webmanifest")
def webmanifest():
    manifest_path = os.path.join(STATIC_DIR, "site.webmanifest")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="application/manifest+json")
    return Response('{"name":"OKPy","icons":[]}', mimetype="application/manifest+json")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
