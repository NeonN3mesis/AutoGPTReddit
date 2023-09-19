"""Reddit API integrations using PRAW."""
import os
import json
import random
import time
from typing import Any, Dict, List, Optional, Tuple, TypedDict, TypeVar

import praw
from auto_gpt_plugin_template import AutoGPTPluginTemplate

from .AutoGPTReddit import AutoGPTReddit

PromptGenerator = TypeVar("PromptGenerator")


class Message(TypedDict):
    role: str
    content: str


class RedditPlugin(AutoGPTPluginTemplate):
    def __init__(self):
        super().__init__()    
        self._name = "autogpt-reddit"
        self._version = "1.1.0"
        self._description = "Reddit API integrations using PRAW."
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.user_agent = os.getenv("REDDIT_USER_AGENT")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.post_id = []
        self.posts = []
        self.api = None
        

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
        return False

    def on_planning(
        self, prompt: PromptGenerator, messages: List[str]
    ) -> Optional[str]:
        """This method is called before the planning chat completeion is done.
        Args:
            prompt (PromptGenerator): The prompt generator.
            messages (List[str]): The list of messages.
        """
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
        pass

    def can_handle_post_command(self) -> bool:
        """This method is called to check that the plugin can
        handle the post_command method.
        Returns:
            bool: True if the plugin can handle the post_command method."""
        return True

    def post_command(self, command_name: str, response: str) -> str:
        current_time = time.time()
        rate_limited = False

        if AutoGPTReddit.rate_limit_reset_time and current_time < AutoGPTReddit.rate_limit_reset_time:
            rate_limited = True

        if AutoGPTReddit.rate_limit_reset_time and current_time >= AutoGPTReddit.rate_limit_reset_time:
            AutoGPTReddit.rate_limit_reset_time = None


        if response:
            try:
                # Assuming 'response' should be a dictionary.
                response_dict = json.loads(response)
                response_dict["Rate limited"] = rate_limited  # Setting the rate_limited flag here
                return json.dumps(response_dict)
            except json.JSONDecodeError:
                # Handle JSON decode error
                return json.dumps({"error": "Invalid JSON response", "rate_limited": rate_limited})
        else:
            return json.dumps({"error": "Empty response", "rate_limited": rate_limited})


 
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
                    "limit": "Number of posts to fetch (default is 10)",
                    "time_filter": 'Time filter for trending posts ("day", "week", "month", "year", "all"; default is "day")',
                },
                lambda **kwargs: reddit_instance.fetch_posts(kwargs),
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
                    "limit": "Number of child comments to fetch (default is all)"
                },
                lambda **kwargs: reddit_instance.fetch_comment_tree(kwargs),
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
                "post_comment",
                "Post a comment. (It's a good idea to make sure you haven't already responded to a comment first.)",
                {
                    "parent_id": "ID of the parent post or comment",
                    "content": "Content of the comment",
                },
                lambda **kwargs: reddit_instance.post_comment(kwargs),
            )
            prompt.add_command(
                "message",
                "Send a message response. (Cannot be used to reply to comments.)",
                {
                    "message_id": "ID of the message",
                    "content": "Content of the response",
                },
                lambda **kwargs: reddit_instance.message(kwargs),
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
                "Read a specific single full notification",
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
            scenex_api_key = os.environ.get("SCENEX_API_KEY")

        if scenex_api_key:
            prompt.add_command(
                "fetch_and_describe_image_post",
                "Fetch an image post and describe the image using SceneXplain",
                {
                    "post_id": "ID of the Reddit post to fetch and describe",
                },
                lambda **kwargs: reddit_instance.fetch_and_describe_image_post(kwargs),

            )
        else:
            print(
                "Warning: SceneXplain API key not set. fetch_and_describe_image_post command is disabled."
            )

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
