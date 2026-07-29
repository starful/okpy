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


if __name__ == "__main__":
    unittest.main()
