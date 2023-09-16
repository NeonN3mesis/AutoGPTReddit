import http.client
import json
import re
import time

import praw
import prawcore
import praw.exceptions



class AutoGPTReddit:
    SUCCESS = "success"
    ERROR = "error"

    
    def set_error_response(self, response, message):
        response["status"] = AutoGPTReddit.ERROR
        response["message"] = message

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
        char_count = 0  # Initialize character count for truncation
        try:
            subreddit_name = args.get("subreddit", "all")
            sort_by = args.get("sort_by", "hot")
            limit = args.get("limit", 10)
            time_filter = args.get("time_filter", "day")

            subreddit = self.reddit.subreddit(subreddit_name)

            # Sort posts
            if sort_by == "hot":
                posts = subreddit.hot(limit=limit)
            elif sort_by == "top":
                posts = subreddit.top(limit=limit, time_filter=time_filter)
            elif sort_by == "new":
                posts = subreddit.new(limit=limit)  # Fetch newest posts
            else:
                posts = subreddit.hot(
                    limit=limit
                )  # Default to hot if sort_by is not recognized

            output = []
            for post in posts:
                if post.selftext or post.url:  # Check if it's a text or link post
                    text = (
                        post.selftext[:200] + "..."
                        if len(post.selftext) > 200
                        else post.selftext
                    )  # Truncate text
                    post_info = {
                        "id": post.id,
                        "title": post.title,
                        "text": text,
                        "score": post.score,
                        "comments_count": post.num_comments,
                    }
                    output.append(post_info)

                    # Check for character count
                    char_count += len(json.dumps(post_info))
                    if char_count >= 2500:
                        break

            response["data"] = output
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)

        return json.dumps(response)

    # Fetches comments from a specified post.
    # args: Dictionary containing 'post_id', 'limit', and 'sort_by' keys.
    def fetch_comments(self, args) -> str:
        response = {"status": "success"}
        char_count = 0  # Initialize character count for truncation
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

            # Replace 'more' comments and fetch the top comments
            submission.comments.replace_more(limit=0)
            comments = submission.comments.list()[:limit]

            output = []
            for comment in comments:
                comment_info = {
                    "Comment ID": comment.id,
                    "Content": comment.body[:200],  # Truncate content
                    "score": comment.score,
                    "Author": str(comment.author),
                }
                output.append(comment_info)

                # Check for character count
                char_count += len(json.dumps(comment_info))
                if char_count >= 2500:
                    break

            response["data"] = output
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)

        return json.dumps(response)

    def post_comment(self, args):
        response = {"status": AutoGPTReddit.SUCCESS}
        
        # Validate arguments
        if not all(k in args for k in ("parent_id", "content")):
            self.set_error_response(response, "Missing required arguments (parent_id, content)")
            return json.dumps(response)
        
        try:
            parent_id = args["parent_id"]
            content = args["content"]
            
            # Determine whether the parent ID corresponds to a comment or a submission
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
            print(f"API Exception Details: {e}")

        except praw.exceptions.ClientException as e:
            self.set_error_response(response, f"Client exception: {str(e)}")
            print(f"Client Exception Details: {e}")

        except Exception as e:
            self.set_error_response(response, f"Unknown exception: {str(e)}")
            print(f"General Exception Details: {e}")

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
                message_type = type(
                    message
                ).__name__  # Get the class name to identify the type
                notification_data.append(
                    {
                        f"{message_type} id": message.id,
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

            # Fetch user's comments
            comments = []
            if char_count < 2500:
                for comment in user.comments.new(limit=10):  # Change limit as needed
                    comment_info = {
                        "id": comment.id,
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
            YOUR_GENERATED_SECRET = (
                "SCENEX_API_KEY"  # Should be read from env variables
            )
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
                "description": description,
            }
        except Exception as e:
            response["status"] = "error"
            response["message"] = str(e)

        return json.dumps(response)
