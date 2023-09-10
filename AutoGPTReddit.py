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
        self.rate_limit_reset_time = (
            None  # Add this line to initialize rate_limit_reset_time
        )

    # Fetches posts from a specified subreddit.
    # args: Dictionary containing 'subreddit', 'limit', and 'sort_by' keys.
    def fetch_posts(self, args):
        subreddit_name = args.get("subreddit", "all")
        limit = args.get("limit", 10)
        sort_by = args.get("sort_by", "hot")
        subreddit = self.reddit.subreddit(subreddit_name)

        if sort_by == "hot":
            posts = subreddit.hot(limit=limit)
        elif sort_by == "new":
            posts = subreddit.new(limit=limit)
        elif sort_by == "top":
            posts = subreddit.top(limit=limit)

        post_data = []
        for post in posts:
            if post.selftext:  # Check if selftext is not empty
                post_data.append(
                    {
                        "id": post.id,
                        "title": post.title,
                        "content": post.selftext,  # Replacing 'content' with 'text'
                        "score": post.score,
                        "comments_count": post.num_comments,
                    }
                )

        return post_data

    # Fetches comments from a specified post.
    # args: Dictionary containing 'post_id', 'limit', and 'sort_by' keys.
    def fetch_comments(self, args):
        post_id = args["post_id"]
        limit = args.get("limit", 10)
        sort_by = args.get(
            "sort_by", "best"
        )  # Options: 'best', 'top', 'new', 'controversial', 'old', 'random', 'qa', 'live'
        post = self.reddit.submission(id=post_id)
        post.comment_sort = sort_by
        post.comments.replace_more(limit=0)
        comments = post.comments.list()[:limit]
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
        return comment_data

    def post_comment(self, args):
        try:
            parent_id = args["parent_id"]
            content = args["content"]
            parent_item = (
                self.reddit.comment(id=parent_id)
                if parent_id.startswith("t1_")
                else self.reddit.submission(id=parent_id)
            )
            new_comment = parent_item.reply(content)
            return {"id": new_comment.id, "message": "Comment posted successfully"}
        except prawcore.exceptions.RequestException as e:
            if "RATELIMIT" in str(e):
                self.rate_limit_reset_time = time.time() + int(
                    e.response.headers.get("x-ratelimit-reset", 0)
                )
                return {
                    "error": "Rate limit exceeded",
                    "remaining_time": e.response.headers.get("x-ratelimit-reset", 0),
                    "rate_limit_active": True,
                }
            return {"error": "An error occurred"}

    def post_thread(self, args):
        try:
            subreddit_name = args["subreddit"]
            title = args["title"]
            content = args["content"]
            subreddit = self.reddit.subreddit(subreddit_name)
            new_post = subreddit.submit(title, selftext=content)
            return {"id": new_post.id, "message": "Thread posted successfully"}
        except prawcore.exceptions.RequestException as e:
            if "RATELIMIT" in str(e):
                self.rate_limit_reset_time = time.time() + int(
                    e.response.headers.get("x-ratelimit-reset", 0)
                )
                return {
                    "error": "Rate limit exceeded",
                    "remaining_time": e.response.headers.get("x-ratelimit-reset", 0),
                    "rate_limit_active": True,
                }
            return {"error": "An error occurred"}

    def vote(self, args):
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
        return {"id": item_id, "action": action}

    def fetch_notifications(self, args):
        limit = min(args.get('limit', 10), 5)  # Set a maximum limit if you want
        unread_messages = list(self.reddit.inbox.unread(limit=limit))
        notification_data = []
        for message in unread_messages:
            truncated_content = message.body[:200]  # Truncate content to the first 100 characters
            notification_data.append({
                'id': message.id,
                'from': message.author.name if message.author else 'Unknown',
                'truncated_content': truncated_content + '...' if len(message.body) > 200 else truncated_content
            })
        return notification_data

    def respond_to_message(self, args):
        message_id = args["message_id"]
        content = args["content"]
        message = self.reddit.message(id=message_id)
        message.reply(content)
        return {"id": message_id, "response_content": content}

    def fetch_trending_posts(self, args):
        subreddit_name = args.get("subreddit", "all")
        limit = args.get("limit", 10)
        sort_by = args.get("sort_by", "hot")
        time_filter = args.get("time_filter", "day")
        subreddit = self.reddit.subreddit(subreddit_name)

        # Fetch posts based on the sort_by criteria
        if sort_by == "hot":
            posts = subreddit.hot(limit=limit)  # Removed time_filter
        elif sort_by == "top":
            posts = subreddit.top(
                limit=limit, time_filter=time_filter
            )  # time_filter is valid here

        # Initialize an empty list to store post data
        post_data = []

        # Loop through each post to extract necessary data
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

        # Return the list of posts
        return post_data

    def fetch_user_profile(self, args):
        username = args["username"]
        user = self.reddit.redditor(username)
        return {
            "id": user.id,
            "name": user.name,
            "karma": user.link_karma + user.comment_karma,
        }

    def fetch_subreddit_info(self, args):
        subreddit_name = args["subreddit"]
        subreddit = self.reddit.subreddit(subreddit_name)
        return {
            "id": subreddit.id,
            "name": subreddit.display_name,
            "subscribers": subreddit.subscribers,
            "description": subreddit.public_description,
        }

    def search_posts(self, args):
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
        return post_data

    def search_comments(self, args):
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
        return comment_data

    def delete_item(self, args):
        item_id = args["id"]
        item = (
            self.reddit.comment(id=item_id)
            if item_id.startswith("t1_")
            else self.reddit.submission(id=item_id)
        )
        item.delete()
        return {"id": item_id, "action": "deleted"}

    def edit_item(self, args):
        item_id = args["id"]
        new_content = args["content"]
        item = (
            self.reddit.comment(id=item_id)
            if item_id.startswith("t1_")
            else self.reddit.submission(id=item_id)
        )
        item.edit(new_content)
        return {"id": item_id, "new_content": new_content}

    def check_rate_limit(self):
        """Check if rate limiting is currently active and if so, how much time is remaining."""
        if self.rate_limit_reset_time:
            remaining_time = self.rate_limit_reset_time - time.time()
            if remaining_time > 0:
                return remaining_time
        return None

    def update_rate_limit_reset_time(self, reset_time_seconds):
        """Update the time when the rate limit will be reset."""
        self.rate_limit_reset_time = time.time() + reset_time_seconds

    def subscribe_subreddit(self, args):
        try:
            subreddit_name = args["subreddit"]
            subreddit = self.reddit.subreddit(subreddit_name)
            subreddit.subscribe()
            return {"message": f"Successfully subscribed to {subreddit_name}"}
        except prawcore.exceptions.RequestException as e:
            return {"error": "An error occurred while subscribing"}

    def get_subscribed_subreddits(self, args=None):
        try:
            limit = (
                int(args.get("limit", 50)) if args else 50
            )  # Set a default limit of 50 if not provided
            subscribed_subreddits = [
                sub.display_name for sub in self.reddit.user.subreddits(limit=limit)
            ]
            return {"subscribed_subreddits": subscribed_subreddits}
        except prawcore.exceptions.RequestException as e:
            if "RATELIMIT" in str(e):
                self.rate_limit_reset_time = time.time() + int(
                    e.response.headers.get("x-ratelimit-reset", 0)
                )
                return {
                    "error": "Rate limit exceeded",
                    "remaining_time": e.response.headers.get("x-ratelimit-reset", 0),
                    "rate_limit_active": True,
                }
            return {"error": "An error occurred"}

    def get_subreddit_info(self, args):
        try:
            subreddit_name = args["subreddit"]
            subreddit = self.reddit.subreddit(subreddit_name)
            return {
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
            return {"error": f"An error occurred: {e}"}

    def get_popular_subreddits(self, args):
        try:
            limit = int(args.get('limit', 50))  # Set a default limit of 50 if not provided
            subreddits = [sub.display_name for sub in self.reddit.subreddit('popular').hot(limit=limit)]
            return {'popular_subreddits': subreddits}
        except Exception as e:
            return {'error': f'An error occurred: {e}'}

    def read_notification(self, args):
        message_id = args['message_id']
        message = self.reddit.message(id=message_id)
        return {
            'id': message.id,
            'content': message.body,
            'from': message.author.name if message.author else 'Unknown',
            # Add any other fields you need
        }