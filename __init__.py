"""Reddit API integrations using PRAW."""
import json
import os
import random
import re
import time
from typing import Any, Dict, List, Optional, Tuple, TypedDict, TypeVar

import praw
from auto_gpt_plugin_template import AutoGPTPluginTemplate
from autogpt.logs.helpers import print_attribute

from .AutoGPTReddit import AutoGPTReddit

PromptGenerator = TypeVar("PromptGenerator")


class Message(TypedDict):
    role: str
    content: str


class RedditPlugin(AutoGPTPluginTemplate):
    def __init__(self):
        super().__init__()
        self._name = "autogpt-reddit"
        self._version = "1.5.0"
        self._description = "Reddit API integrations using PRAW."
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.user_agent = os.getenv("REDDIT_USER_AGENT")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.post_id = []
        self.posts = []
        self.api = None
        can_generate_posts = (
            os.environ.get("CAN_GENERATE_POSTS", "false").lower() == "true"
        )
        scenex_api_key = os.environ.get("SCENEX_API_KEY")

        if (
            self.client_id
            and self.client_secret
            and self.username
            and self.user_agent
            and self.password
        ) is not None:
            # Authenticate to reddit
            self.api = (
                AutoGPTReddit(  # Initialize your own Reddit API wrapper class here
                    self.client_id,
                    self.client_secret,
                    self.user_agent,
                    self.username,
                    self.password,
                )
            )
        else:
            print("Reddit credentials not found in .env file.")
            self.api = None

        if can_generate_posts:
            print(
                "Warning: CAN_GENERATE_POSTS is set to true. submit_post command is enabled."
            )
        else:
            print(
                "Warning: CAN_GENERATE_POSTS is not set to true. submit_post command is disabled."
            )

        if scenex_api_key:
            print("SceneXplain API key set")
        else:
            print(
                "Warning: SceneXplain API key not set. fetch_and_describe_image_post command is disabled."
            )

    rate_limit_reset_time = None

    def can_handle_on_response(self) -> bool:
        """This method is called to check that the plugin can
        handle the on_response method.
        Returns:
            bool: True if the plugin can handle the on_response method."""
        return False

    def on_response(self, response: str, *args, **kwargs) -> str:
        """This method is called when a response is received from the model."""
        pass

    def can_handle_post_prompt(self) -> bool:
        """This method is called to check that the plugin can
        handle the post_prompt method.
        Returns:
            bool: True if the plugin can handle the post_prompt method."""
        return True

    def can_handle_on_planning(self) -> bool:
        """This method is called to check that the plugin can
        handle the on_planning method.
        Returns:
            bool: True if the plugin can handle the on_planning method."""
        return True

    def on_planning(
        self, prompt: PromptGenerator, messages: List[Message]
    ) -> Optional[str]:
        pass

    def can_handle_post_planning(self) -> bool:
        """This method is called to check that the plugin can
        handle the post_planning method.
        Returns:
            bool: True if the plugin can handle the post_planning method."""
        return False

    def post_planning(self, response: str) -> str:
        """This method is called after the planning chat completeion is done.
        Args:
            response (str): The response.
        Returns:
            str: The resulting response.
        """
        pass

    def can_handle_pre_instruction(self) -> bool:
        """This method is called to check that the plugin can
        handle the pre_instruction method.
        Returns:
            bool: True if the plugin can handle the pre_instruction method."""
        return False

    def pre_instruction(self, messages: List[str]) -> List[str]:
        """This method is called before the instruction chat is done.
        Args:
            messages (List[str]): The list of context messages.
        Returns:
            List[str]: The resulting list of messages.
        """
        pass

    def can_handle_on_instruction(self) -> bool:
        """This method is called to check that the plugin can
        handle the on_instruction method.
        Returns:
            bool: True if the plugin can handle the on_instruction method."""
        return False

    def on_instruction(self, messages: List[str]) -> Optional[str]:
        """This method is called when the instruction chat is done.
        Args:
            messages (List[str]): The list of context messages.
        Returns:
            Optional[str]: The resulting message.
        """
        pass

    def can_handle_post_instruction(self) -> bool:
        """This method is called to check that the plugin can
        handle the post_instruction method.
        Returns:
            bool: True if the plugin can handle the post_instruction method."""
        return False

    def post_instruction(self, response: str) -> str:
        """This method is called after the instruction chat is done.
        Args:
            response (str): The response.
        Returns:
            str: The resulting response.
        """
        pass

    def can_handle_pre_command(self) -> bool:
        """This method is called to check that the plugin can
        handle the pre_command method.
        Returns:
            bool: True if the plugin can handle the pre_command method."""
        return False

    def pre_command(
        self, command_name: str, arguments: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """This method is called before the command is executed.
        Args:
            command_name (str): The command name.
            arguments (Dict[str, Any]): The arguments.
        Returns:
            Tuple[str, Dict[str, Any]]: The command name and the arguments.
        """

        # Initialize the Reddit instance from AutoGPTReddit.py
        if self.api:
            reddit_instance = AutoGPTReddit(
                self.client_id,
                self.client_secret,
                self.user_agent,
                self.username,
                self.password,
            )

        # Check for Reddit post IDs in arguments and fetch information
        post_ids = arguments.get("post_ids", [])
        post_info = {}
        for post_id in post_ids:
            post_info[post_id] = reddit_instance.get_post_info(post_id)

        # Check for Reddit comment IDs in arguments and fetch information
        comment_ids = arguments.get("comment_ids", [])
        comment_info = {}
        for comment_id in comment_ids:
            comment_info[comment_id] = reddit_instance.get_comment_info(comment_id)

        # Combine the fetched information based on specified fields
        fetched_info = {}

        if post_info:
            fetched_info["posts"] = {
                post_id: {"title": info["title"], "text": info["text"]}
                for post_id, info in post_info.items()
            }

        if comment_info:
            fetched_info["comments"] = {
                comment_id: {"parent_comments": info["parent_comments"]}
                for comment_id, info in comment_info.items()
            }

        # Append this fetched info to the arguments or handle as needed

        print_attribute(fetched_info)
        return command_name, arguments

    def can_handle_post_command(self) -> bool:
        """This method is called to check that the plugin can
        handle the post_command method.
        Returns:
            bool: True if the plugin can handle the post_command method."""
        return True

    def post_command(self, command_name: str, response: str) -> str:
        current_time = time.time()
        rate_limited_message = "You are not currently rate limited"

        if (
            AutoGPTReddit.rate_limit_reset_time
            and current_time < AutoGPTReddit.rate_limit_reset_time
        ):
            rate_limited_message = "You are rate limited and cannot post or comment"

        if (
            AutoGPTReddit.rate_limit_reset_time
            and current_time >= AutoGPTReddit.rate_limit_reset_time
        ):
            AutoGPTReddit.rate_limit_reset_time = None

        if response:
            try:
                # Assuming 'response' should be a dictionary.
                response_dict = json.loads(response)
                return json.dumps([rate_limited_message, response_dict])
            except json.JSONDecodeError:
                # Handle JSON decode error
                return json.dumps(
                    [rate_limited_message, {"error": "Invalid JSON response"}]
                )
        else:
            return json.dumps([rate_limited_message, {"error": "Empty response"}])

    def can_handle_chat_completion(
        self,
        messages: list[Dict[Any, Any]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> bool:
        """This method is called to check that the plugin can
        handle the chat_completion method.
        Args:
            messages (Dict[Any, Any]): The messages.
            model (str): The model name.
            temperature (float): The temperature.
            max_tokens (int): The max tokens.
        Returns:
            bool: True if the plugin can handle the chat_completion method."""
        return False

    def handle_chat_completion(
        self,
        messages: list[Dict[Any, Any]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """This method is called when the chat completion is done.
        Args:
            messages (Dict[Any, Any]): The messages.
            model (str): The model name.
            temperature (float): The temperature.
            max_tokens (int): The max tokens.
        Returns:
            str: The resulting response.
        """
        return None

    def post_prompt(self, prompt: PromptGenerator) -> PromptGenerator:
        """This method is called just after the generate_prompt is called,
            but actually before the prompt is generated.
        Args:
            prompt (PromptGenerator): The prompt generator.
        Returns:
            PromptGenerator: The prompt generator.
        """

        if self.api:
            reddit_instance = AutoGPTReddit(
                self.client_id,
                self.client_secret,
                self.user_agent,
                self.username,
                self.password,
            )

            prompt.add_command(
                "fetch_posts",
                "Fetch only text and link posts from a subreddit along with IDs, truncated text, and other metadata. Can also fetch trending posts.",
                {
                    "subreddit": 'Name of the subreddit (default is "all")',
                    "sort_by": 'Sorting criteria ("hot", "new", "top"; default is "hot")',
                    "limit": "Number of posts to fetch (default is 20)",
                    "time_filter": 'Time filter for trending posts ("day", "week", "month", "year", "all"; default is "day")',
                },
                lambda **kwargs: reddit_instance.fetch_posts(kwargs),
            )
            prompt.add_command(
                "fetch_post_details",
                "Fetch detailed information of a Reddit post along with its top 3 comments.",
                {
                    "post_id": "ID of the post whose details are to be fetched",
                },
                lambda **kwargs: reddit_instance.fetch_post_details(kwargs),
            )
            prompt.add_command(
                "fetch_comments",
                "Fetch comments from a post along with IDs and other metadata",
                {
                    "post_id": "ID of the post",
                    "limit": "Number of comments to fetch (default is 10)",
                    "sort_by": 'Sorting criteria ("best", "top", "new", "controversial", "old", "random", "qa", "live"; default is "best")',
                },
                lambda **kwargs: reddit_instance.fetch_comments(kwargs),
            )
            prompt.add_command(
                "fetch_comment_tree",
                "Fetch a comment and all its children comments.",
                {
                    "comment_id": "ID of the root comment",
                    "limit": "Number of child comments to fetch (default is all)",
                },
                lambda **kwargs: reddit_instance.fetch_comment_tree(kwargs),
            )
            prompt.add_command(
                "submit_comment",
                "Submit a comment on a post or another comment. (Do not duplicate responses. Check first.)",
                {
                    "parent_id": "ID of the parent post or comment",
                    "content": "Content of the comment",
                },
                lambda **kwargs: reddit_instance.submit_comment(kwargs),
            )
            prompt.add_command(
                "vote",
                "Vote on a post or comment",
                {
                    "id": "ID of the post or comment",
                    "action": 'Vote action ("upvote", "downvote")',
                },
                lambda **kwargs: reddit_instance.vote(kwargs),
            )
            prompt.add_command(
                "fetch_notifications",
                "Fetch unread notifications.",
                {"limit": "Number of notifications to fetch (default is 10)"},
                lambda **kwargs: reddit_instance.fetch_notifications(kwargs),
            )
            prompt.add_command(
                "respond_to_notification",
                "Respond to a notification and mark it as read",
                {
                    "notification_id": "ID of the notification to respond to and mark as read",
                    "reply_content": "The content to reply with",
                },
                lambda **kwargs: reddit_instance.respond_to_notification(kwargs),
            )
            prompt.add_command(
                "subscribe_subreddit",
                "Subscribe to a subreddit",
                {"subreddit": "Name of the subreddit"},
                lambda **kwargs: reddit_instance.subscribe_subreddit(kwargs),
            )
            prompt.add_command(
                "get_subscribed_subreddits",
                "Get a list of subscribed subreddits",
                {},
                lambda **kwargs: reddit_instance.get_subscribed_subreddits(kwargs),
            )
            prompt.add_command(
                "get_subreddit_info",
                "Fetch information about a specific subreddit",
                {"subreddit": "Name of the subreddit"},
                lambda **kwargs: reddit_instance.get_subreddit_info(kwargs),
            )
            prompt.add_command(
                "get_popular_subreddits",
                "Fetch a list of popular subreddits",
                {},
                lambda **kwargs: reddit_instance.get_popular_subreddits(kwargs),
            )
            prompt.add_command(
                "read_notification",
                "Read a specific notification with details",
                {"message_id": "ID of the message to read"},
                lambda **kwargs: reddit_instance.read_notification(kwargs),
            )
            prompt.add_command(
                "fetch_user_profile",
                "Fetches relevant information from a user's profile",
                {
                    "username": "The username of the Reddit user whose profile you want to fetch",
                },
                lambda **kwargs: reddit_instance.fetch_user_profile(kwargs),
            )
            prompt.add_command(
                "search_posts",
                "Search for posts based on a query",
                {
                    "query": "Search query",
                    "limit": "Number of posts to fetch (default is 10)",
                },
                lambda **kwargs: reddit_instance.search_posts(kwargs),
            )
            prompt.add_command(
                "search_comments",
                "Search for comments based on a query",
                {
                    "query": "Search query",
                    "limit": "Number of comments to fetch (default is 10)",
                },
                lambda **kwargs: reddit_instance.search_comments(kwargs),
            )
            prompt.add_constraint(
                {
                    "You are prohibited from creating duplicate content or replying to the same notification twice.",
                }
            )
            prompt.add_constraint(
                {
                    "You are prohibited from reavealing you are AI or non-human.",
                }
            )
            prompt.add_best_practice(
                {
                    "Use fetch_user_profile to check your own activity occasionally so you can dynamically calibrate your plans.",
                }
            )
            prompt.add_best_practice(
                {
                    "Occasionally use fetch-notifications to check your notifications and reply to them. Reply only once to each notification. If you are unsure check your profile first.",
                }
            )
            prompt.add_best_practice(
                {
                    "People on Reddit do not appreciate content from non-humans like bots. Mimic human behavior and do not reveal you are AI.",
                }
            )
            prompt.add_best_practice(
                {
                    "Use different post and comment sorting methods to maximize karma. Sorting by new can be effective.",
                }
            )
            prompt.add_best_practice(
                {
                    "Check your profile, engage with posts, check your subreddits, and find new subreddits.",
                }
            )
            prompt.add_resource(
                {
                    "A full set of non-moderator Reddit commands for interacting with reddit.",
                }
            )
        scenex_api_key = os.environ.get("SCENEX_API_KEY")
        # Conditionally add the fetch_and_describe_image_pos command
        if scenex_api_key:
            prompt.add_command(
                "fetch_and_describe_image_post",
                "Fetch an image post and describe the image using SceneXplain",
                {
                    "post_id": "ID of the Reddit post to fetch and describe",
                },
                lambda **kwargs: reddit_instance.fetch_and_describe_image_post(kwargs),
            )
            prompt.add_resource(
                {
                    "You can access image contents directly with fetch_and_describe_image_post to get fairly accurate descripton of an image."
                }
            )

        can_generate_posts = (
            os.environ.get("CAN_GENERATE_POSTS", "false").lower() == "true"
        )
        # Conditionally add the submit_post command
        if can_generate_posts:
            prompt.add_command(
                "submit_post",
                "Submit a Reddit post",
                {
                    "title": "Title of the post",
                    "content": "Content of the post",
                    "subreddit": "Subreddit to post to",
                },
                lambda **kwargs: reddit_instance.submit_post(kwargs),
            )
        else:
            # Add constraint if can_generate_posts is not true
            prompt.add_constraint(
                {"You are prohibited from generating and submitting posts."}
            )
        current_time = time.time()
        # Add constraint if rate limited
        if (
            AutoGPTReddit.rate_limit_reset_time
            and current_time < AutoGPTReddit.rate_limit_reset_time
        ):
            prompt.add_constraint({"You are rate limited and cannot post or comment"})

        return prompt

    def can_handle_text_embedding(self, text: str) -> bool:
        return False

    def handle_text_embedding(self, text: str) -> list:
        pass

    def can_handle_user_input(self, user_input: str) -> bool:
        return False

    def user_input(self, user_input: str) -> str:
        return user_input

    def can_handle_report(self) -> bool:
        return False

    def report(self, message: str) -> None:
        pass
