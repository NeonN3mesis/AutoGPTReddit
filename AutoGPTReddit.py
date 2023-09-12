import json
import re
import time

import praw
import prawcore


class AutoGPTReddit:
    # Initializes the Reddit API client using PRAW.
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
        )

    # Fetches posts from a specified subreddit.
    # args: Dictionary containing 'subreddit', 'limit', and 'sort_by' keys.
    def fetch_posts(self, args) -> str:
        response = {"status": "success"}
        try:
            subreddit_name = args.get("subreddit", "all")
            sort = args.get("sort_by", "hot")
            limit = args.get("limit", 10)

            subreddit = self.reddit.subreddit(subreddit_name)
            posts = subreddit.hot(limit=limit)  # Fetch posts

            output = []
            for post in posts:
                if post.selftext or post.url:  # Check if it's a text or link post
                    truncated_text = (
                        post.selftext[:100] + "..."
                        if len(post.selftext) > 100
                        else post.selftext
                    )  # Truncate text
                    post_info = {
                        "id": post.id,
                        "title": post.title,
                        "truncated_text": truncated_text,
                        "score": post.score,
                        "comments_count": post.num_comments,
                    }
                    output.append(post_info)

            response["data"] = output
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)

        return json.dumps(response)

    # Fetches comments from a specified post.
    # args: Dictionary containing 'post_id', 'limit', and 'sort_by' keys.
    def fetch_comments(self, args) -> str:
        response = {"status": "success"}
        try:
            post_id = args.get("post_id")
            sort = args.get("sort_by", "best")
            limit = args.get("limit", 10)

            # Initialize post
            submission = self.reddit.submission(id=post_id)

            # Sort comments
            if sort == "best":
                submission.comment_sort = "best"
            elif sort == "new":
                submission.comment_sort = "new"
            elif sort == "top":
                submission.comment_sort = "top"
            # Add other sorting criteria as needed

            output = []
            submission.comments.replace_more(limit=0)
            comments = submission.comments.list()[:limit]

            for comment in comments:
                comment_info = {
                    "Comment ID": comment.id,
                    "Parent ID": comment.parent_id,
                    "Content": comment.body[
                        :100
                    ],  # Truncate content to 100 characters for each comment
                    "Upvotes": comment.ups,
                    "Downvotes": comment.downs,
                    "Subreddit": str(comment.subreddit),
                    "Author": str(comment.author),
                }
                output.append(comment_info)

            response["data"] = output
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)

        return json.dumps(response)

    def post_thread(self, args) -> str:
        response = {"status": "success"}
        try:
            subreddit_name = args["subreddit"]
            title = args["title"]
            content = args["content"]
            subreddit = self.reddit.subreddit(subreddit_name)
            new_post = subreddit.submit(title, selftext=content)
            response["data"] = {
                "id": new_post.id,
                "message": "Thread posted successfully",
            }
        except prawcore.exceptions.RequestException as e:
            if "RATELIMIT" in str(e):
                match = re.search(r"(\\d+) minutes?", str(e))
                if match:
                    minutes = int(match.group(1))
                    self.rate_limit_reset_time = time.time() + minutes * 60
                response["status"] = "error"
                response["message"] = "Rate limit exceeded"
                response["remaining_time"] = minutes * 60
                response["rate_limit_active"] = True
            else:
                response["status"] = "error"
                response["message"] = "An error occurred"

        return json.dumps(response)

    def post_comment(self, args):
        response = {"status": "success"}
        try:
            parent_id = args["parent_id"]
            content = args["content"]
            parent_item = (
                self.reddit.comment(id=parent_id)
                if parent_id.startswith("t1_")
                else self.reddit.submission(id=parent_id)
            )
            comment = parent_item.reply(content)
            response["data"] = {
                "id": comment.id,
                "message": "Comment posted successfully",
            }
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)
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

    def fetch_notifications(self, args):
        response = {"status": "success"}
        try:
            limit = min(args.get("limit", 10), 5)
            unread_messages = list(self.reddit.inbox.unread(limit=limit))
            notification_data = []
            for message in unread_messages:
                truncated_content = message.body[:200]
                notification_data.append(
                    {
                        "id": message.id,
                        "from": message.author.name if message.author else "Unknown",
                        "truncated_content": truncated_content + "..."
                        if len(message.body) > 200
                        else truncated_content,
                    }
                )
            response["data"] = notification_data
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)
        return json.dumps(response)

    def respond_to_message(self, args):
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

    def fetch_trending_posts(self, args):
        response = {'status': 'success'}
        try:
            subreddit_name = args.get("subreddit", "all")
            limit = int(args.get("limit", 10))
            sort_by = args.get("sort_by", "hot")
            time_filter = args.get("time_filter", "day")
            subreddit = self.reddit.subreddit(subreddit_name)

            if sort_by == "hot":
                posts = subreddit.hot(limit=limit)
            elif sort_by == "top":
                posts = subreddit.top(limit=limit, time_filter=time_filter)

            post_data = []
            for post in posts:
                if post.selftext or post.url:  # Check if it's a text or link post
                    truncated_content = post.selftext[:100] + '...' if len(post.selftext) > 100 else post.selftext  # Truncate content to 100 characters
                    post_data.append({
                        "id": post.id,
                        "title": post.title,
                        "truncated_content": truncated_content,  # Using truncated content
                        "score": post.score,
                        "comments_count": post.num_comments,
                    })

            response['data'] = post_data
        except Exception as e:
            response['status'] = 'error'
            response['message'] = str(e)

        return json.dumps(response)

    def fetch_user_profile(self, args):
        response = {"status": "success"}
        try:
            username = args["username"]
            user = self.reddit.redditor(username)
            response["data"] = {
                "id": user.id,
                "name": user.name,
                "karma": user.link_karma + user.comment_karma,
            }
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

    def delete_item(self, args):
        response = {"status": "success"}
        try:
            item_id = args["id"]
            item = (
                self.reddit.comment(id=item_id)
                if item_id.startswith("t1_")
                else self.reddit.submission(id=item_id)
            )
            item.delete()
            response["data"] = {"id": item_id, "action": "deleted"}
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
            limit = int(args.get("limit", 50)) if args else 50
            subscribed_subreddits = [
                sub.display_name for sub in self.reddit.user.subreddits(limit=limit)
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
            message = self.reddit.message(id=message_id)
            response["data"] = {
                "id": message.id,
                "content": message.body,
                "from": message.author.name if message.author else "Unknown",
            }
        except Exception as e:
            response["status"] = "error"
            response["message"] = f"An error occurred: {e}"
        return json.dumps(response)
