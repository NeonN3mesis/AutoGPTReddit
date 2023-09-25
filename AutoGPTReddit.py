import http.client
import json
import os
import re
import time

import praw
import praw.exceptions
import prawcore
from praw.models import MoreComments


class AutoGPTReddit:
    SUCCESS = "success"
    ERROR = "error"
    TRUNCATION_LIMIT = 200  # Constant for truncation limit
    rate_limit_reset_time = None

    @classmethod
    def check_rate_limit(cls):
        current_time = time.time()
        if current_time < cls.rate_limit_reset_time:
            return False, cls.rate_limit_reset_time - current_time
        return True, 0

    def set_error_response(self, response, message):
        response["status"] = AutoGPTReddit.ERROR
        response["error_message"] = message

    def __init__(
        self,
        reddit_app_id,
        reddit_app_secret,
        reddit_user_agent,
        reddit_username,
        reddit_password,
    ):
        self.reddit = praw.Reddit(
            client_id=reddit_app_id,
            client_secret=reddit_app_secret,
            user_agent=reddit_user_agent,
            username=reddit_username,
            password=reddit_password,
            check_for_async=False,
        )

    def fetch_posts(self, args) -> str:
        response = {"status": "success"}
        char_count = 0
        try:
            subreddit_name = args.get("subreddit", "all")
            sort_by = args.get("sort_by", "hot")
            limit = args.get("limit", 10)
            time_filter = args.get("time_filter", "day")

            subreddit = self.reddit.subreddit(subreddit_name)
            if sort_by == "hot":
                posts = subreddit.hot(limit=limit)
            elif sort_by == "top":
                posts = subreddit.top(limit=limit, time_filter=time_filter)
            elif sort_by == "new":
                posts = subreddit.new(limit=limit)
            else:
                posts = subreddit.hot(limit=limit)

            output = []
            for post in posts:
                if post.is_self or (not post.is_self and post.url):
                    text = (
                        post.selftext[:200] + "..."
                        if len(post.selftext) > 200
                        else post.selftext
                    )
                    post_info = {
                        "id": post.id,
                        "title": post.title,
                        "text": text,
                        "score": post.score,
                        "comments_count": post.num_comments,
                    }
                    output.append(post_info)
                    char_count += len(json.dumps(post_info))
                    if char_count >= 2500:
                        break

            response["data"] = output
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)

        return json.dumps(response)

    def fetch_comments(self, args) -> str:
        response = {"status": "success"}
        char_count = 0
        try:
            post_id = args.get("post_id")
            sort = args.get("sort_by", "best")
            limit = args.get("limit", 10)

            submission = self.reddit.submission(id=post_id)
            if sort == "best":
                submission.comment_sort = "best"
            elif sort == "new":
                submission.comment_sort = "new"
            elif sort == "top":
                submission.comment_sort = "top"

            submission.comments.replace_more(limit=0)
            comments = submission.comments.list()[:limit]

            output = []
            for comment in comments:
                comment_info = {
                    "Comment ID": comment.id,
                    "Content": comment.body[:200],
                    "score": comment.score,
                    "Author": str(comment.author),
                }
                output.append(comment_info)
                char_count += len(json.dumps(comment_info))
                if char_count >= 2500:
                    break

            response["data"] = output
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)

        return json.dumps(response)

    def submit_comment(self, args):
        response = {"status": "success"}

        try:
            # Validate arguments
            if not all(k in args for k in ("parent_id", "content")):
                self.set_error_response(
                    response, "Missing required arguments (parent_id, content)"
                )
                return json.dumps(response)

            parent_id = args["parent_id"]
            content = args["content"]

            # Determine parent item
            parent_item = (
                self.reddit.comment(id=parent_id)
                if parent_id.startswith("t1_")
                else self.reddit.submission(id=parent_id)
            )

            # Post the comment
            comment = parent_item.reply(content)

            response["data"] = {
                "id": comment.id,
                "message": "Comment posted successfully",
            }

        except praw.exceptions.APIException as e:
            self.set_error_response(response, f"API exception: {str(e)}")

            # If it's a rate-limit exception, set the rate_limit_reset_time
            if "RATELIMIT" in str(e):
                match = re.search(r"Take a break for (\d+) minutes", str(e))
                if match:
                    minutes = int(match.group(1))
                    AutoGPTReddit.rate_limit_reset_time = time.time() + (minutes * 60)
                else:
                    # Log or handle the case where the expected text was not found in the error message
                    print("Unexpected rate limit message format.")

        except praw.exceptions.ClientException as e:
            self.set_error_response(response, f"Client exception: {str(e)}")

        except Exception as e:
            self.set_error_response(response, f"Unknown exception: {str(e)}")

        return json.dumps(response)

    def submit_post(self, args):
        response = {"status": "success"}

        try:
            # Validate arguments
            if not all(k in args for k in ("title", "content", "subreddit")):
                self.set_error_response(
                    response, "Missing required arguments (title, content, subreddit)"
                )
                return json.dumps(response)

            title = args["title"]
            content = args["content"]
            subreddit_name = args["subreddit"]

            # Getting subreddit object
            subreddit = self.reddit.subreddit(subreddit_name)

            # Check if the subreddit requires flair
            if subreddit.link_flair_position != "none":
                # Fetch available flairs
                available_flairs = list(subreddit.flair.link_templates)
                if available_flairs:
                    flair_options = [
                        {"id": flair["id"], "text": flair["text"]}
                        for flair in available_flairs
                    ]
                    self.set_error_response(
                        response,
                        "This subreddit requires flair. Please pick one and try again.",
                    )
                    response["available_flairs"] = flair_options
                    return json.dumps(response)

            # Submitting the post to the specified subreddit
            submission = subreddit.submit(title, selftext=content)

            response["data"] = {
                "id": submission.id,
                "message": "Post submitted successfully",
            }

        except praw.exceptions.APIException as e:
            self.set_error_response(response, f"API exception: {str(e)}")

            # Handle rate-limiting
            if "RATELIMIT" in str(e):
                match = re.search(r"Take a break for (\d+) minutes", str(e))
                if match:
                    minutes = int(match.group(1))
                    AutoGPTReddit.rate_limit_reset_time = time.time() + (minutes * 60)
                else:
                    print("Unexpected rate limit message format.")

        except praw.exceptions.ClientException as e:
            self.set_error_response(response, f"Client exception: {str(e)}")

        except Exception as e:
            self.set_error_response(response, f"Unknown exception: {str(e)}")

        return json.dumps(response)

    def vote(self, args):
        response = {"status": "success"}
        try:
            item_id = args["id"]
            action = args["action"]
            item = (
                self.reddit.comment(id=item_id)
                if item_id.startswith("t1_")
                else self.reddit.submission(id=item_id)
            )
            if action == "upvote":
                item.upvote()
            elif action == "downvote":
                item.downvote()
            response["data"] = {"id": item_id, "action": action}
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)
        return json.dumps(response)

    def _create_notification_data(self, message):
        content = message.body[: AutoGPTReddit.TRUNCATION_LIMIT]
        should_truncate = len(message.body) > AutoGPTReddit.TRUNCATION_LIMIT
        item_type = "comment" if message.fullname.startswith("t1_") else "message"

        return {
            "id": message.fullname,
            "from": message.author.name if message.author else "Unknown",
            "content": content if not should_truncate else f"{content}...",
            "type": item_type,
        }

    def fetch_notifications(self, args):
        response = {"status": AutoGPTReddit.SUCCESS}
        try:
            limit = min(args.get("limit", 10), 5)
            unread_messages = list(self.reddit.inbox.unread(limit=limit))
            notification_data = [
                self._create_notification_data(message) for message in unread_messages
            ]
            response["data"] = notification_data
        except praw.exceptions.APIException as e:
            self.set_error_response(response, f"API exception: {str(e)}")
        except praw.exceptions.ClientException as e:
            self.set_error_response(response, f"Client exception: {str(e)}")
        except Exception as e:
            self.set_error_response(response, f"Unknown exception: {str(e)}")

        return json.dumps(response)

    def message(self, args):
        response = {"status": "success"}
        try:
            message_id = args["message_id"]
            content = args["content"]
            message = self.reddit.inbox.message(message_id)
            message.reply(content)
            response["data"] = {"id": message_id, "response_content": content}
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)
        return json.dumps(response)

    def fetch_user_profile(self, args) -> str:
        response = {"status": "success"}
        char_count = 0
        try:
            username = args.get("username")
            user = self.reddit.redditor(username)

            # User basic information
            user_data = {
                "id": user.id,
                "name": user.name,
                "karma": user.link_karma + user.comment_karma,
            }

            # Fetch user's posts (submissions)
            posts = []
            for post in user.submissions.new(limit=10):  # Change limit as needed
                post_info = {
                    "id": post.id,
                    "title": post.title,
                    "score": post.score,
                }
                posts.append(post_info)
                char_count += len(json.dumps(post_info))
                if char_count >= 2500:
                    break

            comments = []
            if char_count < 2500:
                for comment in user.comments.new(limit=10):  # Change limit as needed
                    comment_info = {
                        "id": comment.id,
                        "parent_id": comment.parent_id,  # Fetching parent ID
                        "post_id": comment.link_id,  # Fetching post ID
                        "body": comment.body,
                        "score": comment.score,
                    }
                    comments.append(comment_info)
                    char_count += len(json.dumps(comment_info))
                    if char_count >= 2500:
                        break

            # Combine user info, posts, and comments
            user_data["posts"] = posts
            user_data["comments"] = comments

            response["data"] = user_data

        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)

        return json.dumps(response)

    def fetch_subreddit_info(self, args):
        response = {"status": "success"}
        try:
            subreddit_name = args["subreddit"]
            subreddit = self.reddit.subreddit(subreddit_name)
            response["data"] = {
                "id": subreddit.id,
                "name": subreddit.display_name,
                "subscribers": subreddit.subscribers,
                "description": subreddit.public_description,
            }
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)
        return json.dumps(response)

    def search_posts(self, args):
        response = {"status": "success"}
        try:
            query = args["query"]
            limit = args.get("limit", 10)
            posts = self.reddit.subreddit("all").search(query, limit=limit)
            post_data = []
            for post in posts:
                post_data.append(
                    {
                        "id": post.id,
                        "title": post.title,
                        "content": post.selftext,
                        "score": post.score,
                        "comments_count": post.num_comments,
                    }
                )
            response["data"] = post_data
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)
        return json.dumps(response)

    def search_comments(self, args):
        response = {"status": "success"}
        try:
            query = args["query"]
            limit = args.get("limit", 10)
            comments = self.reddit.subreddit("all").search_comments(query, limit=limit)
            comment_data = []
            for comment in comments:
                comment_data.append(
                    {
                        "id": comment.id,
                        "content": comment.body,
                        "score": comment.score,
                        "parent_id": comment.parent_id,
                    }
                )
            response["data"] = comment_data
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)
        return json.dumps(response)

    def subscribe_subreddit(self, args):
        response = {"status": "success"}
        try:
            subreddit_name = args["subreddit"]
            subreddit = self.reddit.subreddit(subreddit_name)
            subreddit.subscribe()
            response["message"] = f"Successfully subscribed to {subreddit_name}"
        except prawcore.exceptions.RequestException as e:
            response["status"] = "error"
            response["message"] = "An error occurred while subscribing"
        return json.dumps(response)

    def get_subscribed_subreddits(self, args=None):
        response = {"status": "success"}
        try:
            subscribed_subreddits = [
                sub.display_name for sub in self.reddit.user.subreddits()
            ]
            response["data"] = {"subscribed_subreddits": subscribed_subreddits}
        except prawcore.exceptions.RequestException as e:
            response["status"] = "error"
            response["message"] = "An error occurred"
        return json.dumps(response)

    def get_subreddit_info(self, args):
        response = {"status": "success"}
        try:
            subreddit_name = args["subreddit"]
            subreddit = self.reddit.subreddit(subreddit_name)
            response["data"] = {
                "id": subreddit.id,
                "name": subreddit.display_name,
                "title": subreddit.title,
                "description": subreddit.description,
                "subscribers": subreddit.subscribers,
                "created_utc": subreddit.created_utc,
                "public_description": subreddit.public_description,
                "over18": subreddit.over18,
                "wiki_enabled": subreddit.wiki_enabled,
            }
        except Exception as e:
            response["status"] = "error"
            response["message"] = f"An error occurred: {e}"
        return json.dumps(response)

    def get_popular_subreddits(self, args):
        response = {"status": "success"}
        try:
            limit = int(args.get("limit", 10))
            subreddit = self.reddit.subreddit("popular")
            posts = subreddit.hot(limit=limit)
            subreddits = [post.subreddit.display_name for post in posts]
            response["data"] = {"popular_subreddits": subreddits}
        except prawcore.exceptions.RequestException as e:
            response["status"] = "error"
            response["message"] = f"An error occurred: {e}"
        return json.dumps(response)

    def read_notification(self, args):
        response = {"status": "success"}
        try:
            message_id = args["message_id"]

            # Determine whether the ID corresponds to a comment or a message
            if message_id.startswith("t1_"):
                message = self.reddit.comment(id=message_id[3:])
                message_type = "comment"
            elif message_id.startswith("t4_"):
                message = self.reddit.inbox.message(message_id[3:])
                message_type = "message"
            else:
                response["status"] = "error"
                response["message"] = "Unknown message type"
                return json.dumps(response)

            response["data"] = {
                "id": message.id,
                "content": message.body,
                "from": message.author.name if message.author else "Unknown",
                "type": message_type,
            }
        except Exception as e:
            response["status"] = "error"
            response["message"] = f"An error occurred: {e}"
        return json.dumps(response)

    def fetch_and_describe_image_post(self, args):
        response = {"status": "success"}
        try:
            post_id = args.get("post_id")
            post = self.reddit.submission(id=post_id)

            if not post.url.lower().endswith((".png", ".jpg", ".jpeg")):
                response["status"] = "error"
                response["message"] = "Not an image post."
                return json.dumps(response)

            # SceneXplain API request
            YOUR_GENERATED_SECRET = os.environ.get("SCENEX_API_KEY")

            data = {
                "data": [
                    {"image": post.url, "features": []},
                ]
            }

            headers = {
                "x-api-key": f"token {YOUR_GENERATED_SECRET}",
                "content-type": "application/json",
            }

            connection = http.client.HTTPSConnection("api.scenex.jina.ai")
            connection.request("POST", "/v1/describe", json.dumps(data), headers)
            api_response = connection.getresponse()
            api_data = json.loads(api_response.read().decode("utf-8"))

            # Extract description
            description = api_data.get("result", [{}])[0].get(
                "text", "No description available."
            )

            # Prepare response
            response["data"] = {
                "id": post.id,
                "title": post.title,
                "text": post.selftext,
                "description": description,
            }
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)

        return json.dumps(response)

    def fetch_comment_tree(self, args) -> str:
        response = {"status": "success"}
        char_count = 0  # Initialize character count for truncation
        try:
            comment_id = args.get("comment_id")
            limit = args.get("limit", 10)  # Limit for child comments

            # Initialize comment
            comment = self.reddit.comment(id=comment_id)

            # Fetch the comment details
            comment_info = {
                "id": comment.id,
                "body": comment.body,
                "score": comment.score,
                "parent_id": comment.parent_id,
            }
            char_count += len(json.dumps(comment_info))

            # Fetch replies (child comments)
            comment.replies.replace_more(limit=0)  # Replace 'more' comments
            replies = []
            for reply in comment.replies.list()[:limit]:
                if isinstance(reply, MoreComments):
                    continue
                reply_info = {
                    "id": reply.id,
                    "body": reply.body,
                    "score": reply.score,
                    "parent_id": reply.parent_id,
                }
                replies.append(reply_info)
                char_count += len(json.dumps(reply_info))
                if char_count >= 2500:
                    break

            # Combine comment info and replies
            comment_info["replies"] = replies

            response["data"] = comment_info

        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)

        return json.dumps(response)
