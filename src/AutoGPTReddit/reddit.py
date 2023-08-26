import praw

def authenticate_reddit(client_id, client_secret, username, user_agent, password):
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        user_agent=user_agent,
        password=password
    )

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
        comments.append({
            'id': comment.id,
            'text': comment.body,
        })
    return comments

def submit_post(api, subreddit, title, text):
    subreddit = api.subreddit(subreddit)
    return subreddit.submit(title, selftext=text).id

def submit_comment_on_post(api, post_id, text):
    submission = api.submission(id=post_id)
    return submission.reply(text).id

def reply_to_comment(api, comment_id, text):
    comment = api.comment(id=comment_id)
    return comment.reply(text).id

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

def upvote(api, object_id, object_type):
    if object_type == "post":
        submission = api.submission(id=object_id)
        submission.upvote()
    elif object_type == "comment":
        comment = api.comment(id=object_id)
        comment.upvote()

def downvote(api, object_id, object_type):
    if object_type == "post":
        submission = api.submission(id=object_id)
        submission.downvote()
    elif object_type == "comment":
        comment = api.comment(id=object_id)
        comment.downvote()

def search_reddit_user(api, username):
    user = api.redditor(username)
    return {
        'username': user.name,
        'karma': user.link_karma + user.comment_karma,
        'is_gold': user.is_gold,
        'is_mod': user.is_mod,
        'has_verified_email': user.has_verified_email,
        'created_utc': user.created_utc
    }

def get_user_info(api, username):
    user = api.redditor(username)
    return {
        'username': user.name,
        'karma': user.link_karma + user.comment_karma,
        'is_gold': user.is_gold,
        'is_mod': user.is_mod,
        'has_verified_email': user.has_verified_email,
        'created_utc': user.created_utc,
        'comment_karma': user.comment_karma,
        'link_karma': user.link_karma,
        'is_employee': user.is_employee,
        'is_friend': user.is_friend,
        'is_suspended': user.is_suspended
    }

def get_subreddit_info(api, subreddit_name):
    subreddit = api.subreddit(subreddit_name)
    return {
        'display_name': subreddit.display_name,
        'title': subreddit.title,
        'description': subreddit.description,
        'subscribers': subreddit.subscribers,
        'created_utc': subreddit.created_utc
    }

def get_notifications(api):
    notifications = []
    for item in api.inbox.unread(limit=10):
        if isinstance(item, praw.models.Message):
            notifications.append({
                'type': 'Message',
                'from': item.author.name if item.author else 'Unknown',
                'subject': item.subject,
                'body': item.body
            })
        elif isinstance(item, praw.models.Comment):
            notifications.append({
                'type': 'Comment',
                'from': item.author.name if item.author else 'Unknown',
                'body': item.body
            })
    return notifications
# TODO: Additional functionalities (Edit, Delete, Save/Unsave) can be implemented here

def get_top_level_comments(api, post_id, limit=10):
    submission = api.submission(post_id)
    submission.comments.replace_more(limit=0)
    top_level_comments = [comment.body for comment in submission.comments[:limit]]
    return top_level_comments

def get_all_comments(api, post_id, sort='new', limit=10):
    submission = api.submission(post_id)
    submission.comment_sort = sort
    submission.comments.replace_more(limit=0)
    all_comments = [comment.body for comment in submission.comments.list()[:limit]]
    return all_comments
