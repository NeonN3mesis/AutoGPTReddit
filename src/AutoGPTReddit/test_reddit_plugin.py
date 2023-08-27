import os
import unittest
from unittest.mock import patch
from .reddit import (
    authenticate_reddit,
    get_notifications,
    get_posts_from_subreddit,
    submit_post
)

MOCK_USERNAME = "example_reddit_user"
MOCK_SUBREDDIT = "example_subreddit"
MOCK_TITLE = "Example Title"
MOCK_TEXT = "Example Text"


class TestRedditPlugin(unittest.TestCase):
    def setUp(self):
        os.environ["REDDIT_CLIENT_ID"] = "example_client_id"
        os.environ["REDDIT_CLIENT_SECRET"] = "example_client_secret"
        os.environ["REDDIT_USERNAME"] = MOCK_USERNAME
        os.environ["REDDIT_USER_AGENT"] = "example_user_agent"
        os.environ["REDDIT_PASSWORD"] = "example_password"

    def tearDown(self):
        os.environ.pop("REDDIT_CLIENT_ID", None)
        os.environ.pop("REDDIT_CLIENT_SECRET", None)
        os.environ.pop("REDDIT_USERNAME", None)
        os.environ.pop("REDDIT_USER_AGENT", None)
        os.environ.pop("REDDIT_PASSWORD", None)

    def test_authenticate_reddit(self):
        with patch('praw.Reddit') as MockReddit:
            self.assertIsInstance(authenticate_reddit(
                os.environ["REDDIT_CLIENT_ID"],
                os.environ["REDDIT_CLIENT_SECRET"],
                os.environ["REDDIT_USERNAME"],
                os.environ["REDDIT_USER_AGENT"],
                os.environ["REDDIT_PASSWORD"]
            ), MockReddit)

    def test_get_notifications(self):
        with patch('praw.Reddit') as MockReddit:
            api = MockReddit()
            self.assertIsInstance(get_notifications(api, limit=5), list)

    def test_get_posts_from_subreddit(self):
        with patch('praw.Reddit') as MockReddit:
            api = MockReddit()
            self.assertIsInstance(get_posts_from_subreddit(api, MOCK_SUBREDDIT, 5), list)

    def test_submit_post(self):
        with patch('praw.Reddit') as MockReddit:
            api = MockReddit()
            self.assertIsInstance(submit_post(api, MOCK_SUBREDDIT, MOCK_TITLE, MOCK_TEXT), str)


if __name__ == "__main__":
    unittest.main()
