import praw

def get_posts_from_subreddit(api, subreddit, number_of_posts=10):
    subreddit = api.subreddit(subreddit)
    posts = []
    for post in subreddit.hot(limit=number_of_posts):
        posts.append({
            'id': post.id,
            'title': post.title,
        })
    return posts

def get_comments_on_post(api, post_id, number_of_comments):
    submission = api.submission(id=post_id)
    submission.comments.replace_more(limit=0)
    comments = []
    for comment in submission.comments.list()[:number_of_comments]:
        comments.append(comment.body)
    return comments

def submit_post(api, subreddit, title, text):
    subreddit = api.subreddit(subreddit)
    return subreddit.submit(title, selftext=text)

def submit_comment_on_post(api, post_id, text):
    submission = api.submission(id=post_id)
    return submission.reply(text)

def reply_to_comment(api, comment_id, text):
    comment = api.comment(id=comment_id)
    return comment.reply(text)

def search_reddit(api, query, subreddit=None, number_of_posts=10):
    if subreddit:
        subreddit = api.subreddit(subreddit)
        results = subreddit.search(query, limit=number_of_posts)
    else:
        results = api.subreddit("all").search(query, limit=number_of_posts)
    posts = []
    for post in results:
        posts.append({
            'id': post.id,
            'title': post.title,
        })
    return posts

def upvote(api, post_id, object_type):
    if object_type == 'post':
        submission = api.submission(id=post_id)
        submission.upvote()
    elif object_type == 'comment':
        comment = api.comment(id=post_id)
        comment.upvote()

def downvote(api, post_id, object_type):
    if object_type == 'post':
        submission = api.submission(id=post_id)
        submission.downvote()
    elif object_type == 'comment':
        comment = api.comment(id=post_id)
        comment.downvote()

def search_reddit_user(api, username):
    redditor = api.redditor(username)
    return f"Username: {redditor.name}, Karma: {redditor.comment_karma + redditor.link_karma}"


# TODO: Additional functionalities (Edit, Delete, Save/Unsave) can be implemented here
