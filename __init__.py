"""Reddit API integrations using PRAW."""
import os
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
        self._version = "0.2.0"
        self._description = "Reddit API integrations using PRAW."
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.username = os.getenv("REDDIT_USERNAME")
        self.user_agent = os.getenv("REDDIT_USER_AGENT")
        self.password = os.getenv("REDDIT_PASSWORD")
        self.post_id = []
        self.posts = []
        self.api = None
        self.redditdelay_min = int(os.getenv("REDDITDELAY_MIN", 0))
        self.redditdelay_max = int(os.getenv("REDDITDELAY_MAX", 0))
        # Error checking to ensure REDDITDELAY_MAX is greater than or equal to REDDITDELAY_MIN
        if self.redditdelay_max < self.redditdelay_min:
            print(
                "Error: REDDITDELAY_MAX must be greater than or equal to REDDITDELAY_MIN."
            )
            self.redditdelay_max = self.redditdelay_min

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
                password=self.password,
            )
        else:
            print("Reddit credentials not found in .env file.")

    def apply_randomized_delay(self):
        # Your randomized delay logic here
        delay_time = random.randint(self.redditdelay_min, self.redditdelay_max)
        print(f"Applying randomized delay for {delay_time} seconds...")
        for i in range(delay_time, 0, -1):
            print(f"Next cycle in {i} seconds...")
            time.sleep(1)

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
            reddit_instance = AutoGPTReddit()

            # New core commands
            prompt.add_command(
                "reddit_interaction",
                "Interact with Reddit posts, comments, and more",
                {
                    "type": "<type>",
                    "action": "<action>",
                    "subreddit_name": "<subreddit_name>",
                    "post_id": "<post_id>",
                    "comment_id": "<comment_id>",
                    "text": "<text>",
                    "number": "<number>",
                    "flair_id": "<flair_id>",
                    "is_sticky": "<is_sticky>",
                    "sort": "<sort>",
                    "multi_name": "<multi_name>",
                    "multi_subs": "<multi_subs>",
                    "visibility": "<visibility>",
                },
                lambda **kwargs: reddit_instance.reddit_interaction(self.api, **kwargs),
            )
            prompt.add_command(
                "reddit_vote_save",
                "Vote or save Reddit posts or comments",
                {
                    "action": "<action>",
                    "post_id": "<post_id>",
                    "object_type": "<object_type>",
                },
                lambda **kwargs: reddit_instance.reddit_vote_save(self.api, **kwargs),
            )
        prompt.add_command(
            "reddit_notifications_messages",
            "Retrieve notifications or send messages",
            {
                "action": "<action>",
                "recipient": "<recipient>",
                "subject": "<subject>",
                "message_body": "<message_body>",
            },
            lambda **kwargs: reddit_instance.reddit_notifications_messages(
                self.api, **kwargs
            ),
        )
        prompt.add_command(
            "reddit_search_trends",
            "Search Reddit or get trending posts",
            {
                "action": "<action>",
                "query": "<query>",
                "subreddit": "<subreddit>",
                "number_of_posts": "<number_of_posts>",
            },
            lambda **kwargs: reddit_instance.reddit_search_trends(self.api, **kwargs),
        )
        prompt.add_command(
            "reddit_preferences",
            "Change user preferences",
            {"action": "<action>", "sort_type": "<sort_type>"},
            lambda **kwargs: reddit_instance.reddit_preferences(self.api, **kwargs),
        )
        prompt.add_command(
            "reddit_saved",
            "Retrieve saved items",
            {},
            lambda: reddit_instance.reddit_saved(self.api),
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
