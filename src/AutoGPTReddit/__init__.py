"""Reddit API integrations using PRAW."""
import os
from typing import Any, Dict, List, Optional, Tuple, TypedDict, TypeVar

import praw
from .reddit import *
from auto_gpt_plugin_template import AutoGPTPluginTemplate

PromptGenerator = TypeVar("PromptGenerator")


class Message(TypedDict):
    role: str
    content: str


class AutoGPTReddit(AutoGPTPluginTemplate):
    """
    Reddit API integrations using PRAW
    """

    def __init__(self):
        super().__init__()
        self._name = "autogpt-reddit"
        self._version = "0.0.4"
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
            self.api = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                username=self.username,
                user_agent=self.user_agent,
                password=self.password
            )
        else:
            print("Reddit credentials not found in .env file.")

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
        return False

    def post_command(self, command_name: str, response: str) -> str:
        """This method is called after the command is executed.
        Args:
            command_name (str): The command name.
            response (str): The response.
        Returns:
            str: The resulting response.
        """
        pass

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
            from .reddit import (
                get_posts_from_subreddit,
                get_comments_on_post,
                submit_post,
                submit_comment_on_post,
                reply_to_comment,
                search_reddit,
                upvote,
                downvote,
                search_reddit_user,
                get_top_level_comments,
                get_all_comments,
                get_notifications,
                send_message,
                get_trending_posts,
                get_my_subreddits,
                join_subreddit,
                get_notifications
            )
            prompt.add_command(
    "submit_post",
    "Submit a post",
    {
        "subreddit": "<subreddit>",
        "title": "<title>",
        "text": "<text>",
        "flair_id": "<flair_id>"
    },
    lambda subreddit, title, text, flair_id=None: submit_post(self.api, subreddit, title, text, flair_id)
)
            prompt.add_command(
    "get_comments_on_post",
    "Get comments on a post",
    {"post_id": "<post_id>", "number_of_comments": "<number_of_comments>"},
    lambda post_id, number_of_comments: get_comments_on_post(self.api, post_id, int(number_of_comments))
)
            prompt.add_command(
    "submit_comment_on_post",
    "Submit a comment on a post",
    {"post_id": "<post_id>", "text": "<text>"},
    lambda post_id, text: submit_comment_on_post(self.api, post_id, text)
)
            prompt.add_command(
    "reply_to_comment",
    "Reply to a comment",
    {"comment_id": "<comment_id>", "text": "<text>"},
    lambda comment_id, text: reply_to_comment(self.api, comment_id, text)
)
            prompt.add_command(
    "search_reddit",
    "Search reddit",
    {"query": "<query>", "subreddit": "<subreddit>", "number_of_posts": "<number_of_posts>"},
    lambda query, subreddit, number_of_posts: search_reddit(self.api, query, subreddit, int(number_of_posts))
)
            prompt.add_command(
    "upvote",
    "Upvote a post or comment",
    {"post_id": "<post_id>", "object_type": "<object_type>"},
    lambda post_id, object_type: upvote(self.api, post_id, object_type)
)
            prompt.add_command(
    "downvote",
    "Downvote a post or comment",
    {"post_id": "<post_id>", "object_type": "<object_type>"},
    lambda post_id, object_type: downvote(self.api, post_id, object_type)
)
            prompt.add_command(
    "search_reddit_user",
    "Get user information",
    {"username": "<username>"},
    lambda username: search_reddit_user(self.api, username)
)
            prompt.add_command(
    "get_top_level_comments",
    "Get top-level comments from a Reddit post",
    {"post_id": "<post_id>", "limit": "<limit>"},
    lambda post_id, limit: get_top_level_comments(self.api, post_id, int(limit))
)
            prompt.add_command(
    "get_all_comments",
    "Get all comments from a Reddit post, sorted according to the given parameter",
    {"post_id": "<post_id>", "sort": "<sort>", "limit": "<limit>"},
    lambda post_id, sort, limit: get_all_comments(self.api, post_id, sort, int(limit))
)
            prompt.add_command(
    "get_notifications",
    "Retrieve unread Reddit notifications",
    {},  # No additional arguments are needed
    lambda: get_notifications(self.api)
)
            prompt.add_command(
    "send_message",
    "Send a Reddit message",
    {"recipient": "<recipient>", "subject": "<subject>", "message_body": "<message_body>"},
    lambda recipient, subject, message_body: send_message(self.api, recipient, subject, message_body)
)
            prompt.add_command(
    "edit_comment",
    "Edit an existing comment",
    {"comment_id": "<comment_id>", "new_text": "<new_text>"},
    lambda comment_id, new_text: edit_comment(self.api, comment_id, new_text)
)

            prompt.add_command(
    "delete_comment",
    "Delete a comment",
    {"comment_id": "<comment_id>"},
    lambda comment_id: delete_comment(self.api, comment_id)
)

            prompt.add_command(
    "save_comment",
    "Save a comment",
    {"comment_id": "<comment_id>"},
    lambda comment_id: save_comment(self.api, comment_id)
)
            prompt.add_command(
    "get_trending_posts",
    "Get a list of the top 5 hot and top 5 rising posts on Reddit",
    {},
    lambda: get_trending_posts(self.api)
)
            prompt.add_command(
    "get_my_subreddits",
    "Get a list of subreddits the authenticated user is a part of along with ban status",
    {},
    lambda: get_my_subreddits(self.api)
)
            prompt.add_command(
    "join_subreddit",
    "Join a subreddit",
    {"subreddit_name": "<subreddit_name>"},
    lambda subreddit_name: join_subreddit(self.api, subreddit_name)
)               
            prompt.add_command(
    "get_top_level_comments",
    "Get top-level comments from a Reddit post",
    {"post_id": "<post_id>", "limit": "<limit>"},
    lambda post_id, limit: get_top_level_comments(self.api, post_id, int(limit))
)
            prompt.add_command(
    "get_all_comments",
    "Get all comments from a Reddit post, sorted according to the given parameter",
    {"post_id": "<post_id>", "sort": "<sort>", "limit": "<limit>"},
    lambda post_id, sort, limit: get_all_comments(self.api, post_id, sort, int(limit))
)
            prompt.add_command(
    "get_notifications",
    "Retrieve unread Reddit notifications",
    {},  # No additional arguments are needed
    lambda: get_notifications(self.api)
)
        return prompt

    def can_handle_text_embedding(
        self, text: str
    ) -> bool:
        return False
    
    def handle_text_embedding(
        self, text: str
    ) -> list:
        pass
    
    def can_handle_user_input(self, user_input: str) -> bool:
        return False

    def user_input(self, user_input: str) -> str:
        return user_input

    def can_handle_report(self) -> bool:
        return False

    def report(self, message: str) -> None:
        pass
