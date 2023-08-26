
import praw

# Function to fetch latest posts from a subreddit
def get_posts_from_subreddit(api, subreddit, number_of_posts=10):
    return [post.title for post in api.subreddit(subreddit).new(limit=number_of_posts)]

# Function to search for content on Reddit
def search_reddit(api, query, subreddit=None, number_of_posts=10):
    return [post.title for post in api.subreddit(subreddit).search(query, limit=number_of_posts)]

# Function to fetch top comments from a post
def get_comments_on_post(api, post_id, number_of_comments=10):
    post = api.submission(id=post_id)
    return [comment.body for comment in post.comments[:number_of_comments]]

# Function to post content to a subreddit
def submit_post(api, subreddit, title, text):
    return api.subreddit(subreddit).submit(title=title, selftext=text)

# Function to comment on a post
def submit_comment_on_post(api, post_id, text):
    post = api.submission(id=post_id)
    return post.reply(text)

# Function to reply to a comment
def reply_to_comment(api, comment_id, text):
    comment = api.comment(id=comment_id)
    return comment.reply(text)

# Function to upvote a post or comment
def upvote(api, object_id, object_type):
    if object_type == 'post':
        post = api.submission(id=object_id)
        return post.upvote()
    elif object_type == 'comment':
        comment = api.comment(id=object_id)
        return comment.upvote()

# Function to downvote a post or comment
def downvote(api, object_id, object_type):
    if object_type == 'post':
        post = api.submission(id=object_id)
        return post.downvote()
    elif object_type == 'comment':
        comment = api.comment(id=object_id)
        return comment.downvote()

# Function to search for user-specific content
def search_reddit_user(api, username):
    user = api.redditor(username)
    return {
        'name': user.name,
        'link_karma': user.link_karma,
        'comment_karma': user.comment_karma,
    }

# TODO: Additional functionalities (Edit, Delete, Save/Unsave) can be implemented here
