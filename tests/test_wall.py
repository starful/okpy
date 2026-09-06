import json
import os
import tempfile
import unittest

from app import app
import app.wall as wall


class WallPagesTest(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self._tmpdir = tempfile.TemporaryDirectory()
        self.queue = os.path.join(self._tmpdir.name, "queue.json")
        self._orig_queue = wall.QUEUE_JSON
        wall.QUEUE_JSON = self.queue

    def tearDown(self):
        wall.QUEUE_JSON = self._orig_queue
        self._tmpdir.cleanup()

    def test_wall_page_lists_approved(self):
        resp = self.client.get("/wall")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("ウォール", html)
        self.assertIn("ひとこと", html)
        self.assertIn("github.com/starful/okpy", html)
        self.assertIn('id="wall-form"', html)

    def test_home_shows_three_wall_cards(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        html = home.get_data(as_text=True)
        self.assertIn('id="wall"', html)
        wall_html = html.split('id="wall"', 1)[-1].split('id="latest"', 1)[0]
        self.assertEqual(wall_html.count('class="wall-card wall-card--'), 3)

    def test_post_valid_memo_queues(self):
        resp = self.client.post(
            "/wall",
            data={
                "type": "memo",
                "text": "ローカルでウォール投稿の確認をした",
                "url": "",
                "name": "tester",
                "website": "",
            },
        )
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("確認待ち", html)
        with open(self.queue, encoding="utf-8") as fh:
            queued = json.loads(fh.read())
        self.assertEqual(len(queued["items"]), 1)
        self.assertEqual(queued["items"][0]["type"], "memo")
        self.assertEqual(queued["items"][0]["status"], "pending")

    def test_honeypot_rejected(self):
        resp = self.client.post(
            "/wall",
            data={
                "type": "memo",
                "text": "これはボットの投稿ですよ",
                "name": "bot",
                "website": "http://spam.example",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("送信できませんでした", resp.get_data(as_text=True))
        self.assertFalse(os.path.isfile(self.queue))

    def test_github_url_rejected(self):
        resp = self.client.post(
            "/wall",
            data={
                "type": "github",
                "text": "リポジトリを置いてみる",
                "url": "https://example.com/not-github",
                "name": "tester",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("GitHub", resp.get_data(as_text=True))
        self.assertFalse(os.path.isfile(self.queue))


class WallValidateTest(unittest.TestCase):
    def test_github_ok(self):
        fields, err = wall.validate_submission(
            kind="github",
            text="okpy のソースです",
            url="https://github.com/starful/okpy",
            name="starful",
            honeypot="",
        )
        self.assertEqual(err, "")
        self.assertEqual(fields["url"], "https://github.com/starful/okpy")

    def test_http_rejected(self):
        fields, err = wall.validate_submission(
            kind="ship",
            text="つくったものを置きます",
            url="http://okpy.net/",
            name="",
            honeypot="",
        )
        self.assertIsNone(fields)
        self.assertIn("https", err)


if __name__ == "__main__":
    unittest.main()
