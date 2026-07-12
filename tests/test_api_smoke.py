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

        post = self.client.get("/blog/sample-python-pydantic")
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


if __name__ == "__main__":
    unittest.main()
