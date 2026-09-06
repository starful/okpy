import unittest

from app import app


class BlogSmokeTest(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_and_blog_post(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn(b"OKPy", home.data)

        post = self.client.get(
            "/blog/pythonのデータバリデーション決定版-pydantic-v2の使い方とメリットを徹底解説"
        )
        self.assertEqual(post.status_code, 200)

    def test_category_pages(self):
        for cat in ("python", "cloud"):
            resp = self.client.get(f"/category/{cat}")
            self.assertEqual(resp.status_code, 200)

    def test_robots_and_sitemap_exist(self):
        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertIn("Sitemap:", robots.get_data(as_text=True))

        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        body = sitemap.get_data(as_text=True)
        self.assertIn("<urlset", body)
        self.assertIn("/blog/", body)

    def test_legacy_routes_redirect(self):
        guide = self.client.get("/guide", follow_redirects=False)
        self.assertEqual(guide.status_code, 301)

        # Hatena soft-duplicates and dead surfaces
        page = self.client.get("/?page=1771459201", follow_redirects=False)
        self.assertEqual(page.status_code, 301)
        self.assertEqual(page.headers.get("Location"), "/")

        archive = self.client.get("/archive/2025/03/17", follow_redirects=False)
        self.assertEqual(archive.status_code, 301)
        self.assertEqual(archive.headers.get("Location"), "/")

        archive_cat = self.client.get(
            "/archive/category/Data%20Model", follow_redirects=False
        )
        self.assertEqual(archive_cat.status_code, 301)
        self.assertEqual(archive_cat.headers.get("Location"), "/category/data-model")

        rss = self.client.get("/rss/category/x", follow_redirects=False)
        self.assertEqual(rss.status_code, 301)
        self.assertEqual(rss.headers.get("Location"), "/")

        # Unmapped entry collapses to home
        entry = self.client.get("/entry/2099/01/01/000000", follow_redirects=False)
        self.assertEqual(entry.status_code, 301)
        self.assertEqual(entry.headers.get("Location"), "/")

        # Mapped entry still goes to /blog/...
        from app import REDIRECT_MAP

        if REDIRECT_MAP:
            old = next(iter(REDIRECT_MAP))
            mapped = self.client.get(old, follow_redirects=False)
            self.assertEqual(mapped.status_code, 301)
            self.assertIn("/blog/", mapped.headers.get("Location", ""))

    def test_career_category_and_post(self):
        listing = self.client.get("/category/career")
        self.assertEqual(listing.status_code, 200)
        html = listing.get_data(as_text=True)
        self.assertIn("/category/career/mbti", html)
        self.assertIn("/blog/ai_engineer", html)

        post = self.client.get("/blog/ai_engineer")
        self.assertEqual(post.status_code, 200)
        post_html = post.get_data(as_text=True)
        self.assertNotIn("Starful", post_html)
        self.assertIn("ok-project-assets/okpy/career/ai_engineer.jpg", post_html)

    def test_career_excluded_from_home_mixed_feed(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        html = home.get_data(as_text=True)
        latest = html.split('id="latest"', 1)[-1].split('id="topics"', 1)[0]
        self.assertNotIn("/blog/ai_engineer", latest)
        self.assertNotIn("/blog/ios_engineer", latest)
        self.assertEqual(latest.count('class="story-card"'), 4)
        import re

        latest_cats = re.findall(r'data-cat="([^"]+)"', latest)
        self.assertEqual(len(latest_cats), 4)
        self.assertEqual(len(set(latest_cats)), 4)
        self.assertNotIn('id="popular"', html)
        self.assertNotIn("人気の記事", html)
        self.assertIn('id="cat-career"', html)
        self.assertIn("/category/career/mbti", html)
        self.assertIn("MBTIから探すIT職種", html)
        self.assertIn("home-toc", html)
        self.assertIn('id="trends"', html)
        self.assertIn("AIスキル・概念", html)
        self.assertIn("クラウドサービス", html)
        self.assertIn("ITビジネス", html)
        self.assertIn("trend-board--skills", html)
        self.assertIn("trend-board--cloud", html)
        self.assertIn("trend-board--biz", html)
        self.assertNotIn("開発言語", html)
        self.assertNotIn("trend-board--languages", html)
        self.assertEqual(html.count('class="trend-item'), 36)
        self.assertIn("is-top1", html)
        special_to_latest = html.split('id="special"', 1)[-1].split('id="latest"', 1)[0]
        self.assertIn('id="trends"', special_to_latest)
        self.assertIn('id="wall"', special_to_latest)
        self.assertIn("置く / すべて見る", special_to_latest)
        self.assertEqual(special_to_latest.count('class="wall-card wall-card--'), 3)
        cat_order = html.split('id="cat-')
        self.assertGreater(len(cat_order), 3)
        self.assertTrue(cat_order[1].startswith("eng-comms"))
        self.assertTrue(cat_order[2].startswith("data-analysis"))
        self.assertIn("Business Analysis", html)
        import re

        career_section = re.search(
            r'<section class="section" id="cat-career">.*?</section>',
            html,
            re.S,
        )
        self.assertIsNotNone(career_section)
        self.assertEqual(career_section.group(0).count('class="story-card"'), 3)

    def test_home_shows_all_categories_three_each(self):
        from app.config import SITE_CONFIG

        home = self.client.get("/")
        html = home.get_data(as_text=True)
        for cat in SITE_CONFIG["blog_categories"]:
            self.assertIn(f'id="cat-{cat}"', html)

    def test_career_mbti_nested_routes(self):
        index = self.client.get("/category/career/mbti")
        self.assertEqual(index.status_code, 200)
        index_html = index.get_data(as_text=True)
        self.assertIn("INTJ", index_html)
        self.assertIn("/category/career/mbti/INTJ", index_html)
        self.assertNotIn("Starful", index_html)

        type_page = self.client.get("/category/career/mbti/INTJ")
        self.assertEqual(type_page.status_code, 200)
        type_html = type_page.get_data(as_text=True)
        self.assertIn("/blog/", type_html)
        self.assertNotIn("Starful", type_html)

        missing = self.client.get("/category/career/mbti/XXXX")
        self.assertEqual(missing.status_code, 404)

    def test_sitemap_includes_career_and_mbti(self):
        sitemap = self.client.get("/sitemap.xml")
        body = sitemap.get_data(as_text=True)
        self.assertIn("/category/career", body)
        self.assertIn("/category/career/mbti", body)
        self.assertIn("/category/career/mbti/INTJ", body)
        self.assertIn("/blog/ai_engineer", body)
        self.assertIn("/wall", body)


if __name__ == "__main__":
    unittest.main()
