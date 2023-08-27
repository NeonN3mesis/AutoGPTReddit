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

def get_notifications(api, limit=10):
    notifications = []
    for item in api.inbox.unread(limit=limit):
        if isinstance(item, praw.models.Message):
            notifications.append({
                'id': item.id,
                'type': 'Message',
                'from': item.author.name if item.author else 'Unknown',
                'subject': item.subject,
                'body': item.body
            })
        elif isinstance(item, praw.models.Comment):
            notifications.append({
                'id': item.id,
                'type': 'Comment',
                'from': item.author.name if item.author else 'Unknown',
                'body': item.body
            })
    return notifications

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

def send_message(api, recipient, subject, message_body):
    redditor = api.redditor(recipient)
    redditor.message(subject, message_body)
    return f"Message sent to {recipient}"

def edit_comment(api, comment_id, new_text):
    comment = api.comment(id=comment_id)
    comment.edit(new_text)
    return f"Comment {comment_id} edited."

def delete_comment(api, comment_id):
    comment = api.comment(id=comment_id)
    comment.delete()
    return f"Comment {comment_id} deleted."

def save_comment(api, comment_id):
    comment = api.comment(id=comment_id)
    comment.save()
    return f"Comment {comment_id} saved."

def get_trending_posts(api):
    subreddit = api.subreddit("all")
    hot_posts = []
    rising_posts = []
    
    for post in subreddit.hot(limit=5):
        hot_posts.append({
            'id': post.id,
            'title': post.title,
            'subreddit': post.subreddit.display_name,
            'upvotes': post.score,
            'comments': post.num_comments
        })

    for post in subreddit.rising(limit=5):
        rising_posts.append({
            'id': post.id,
            'title': post.title,
            'subreddit': post.subreddit.display_name,
            'upvotes': post.score,
            'comments': post.num_comments
        })

    return {'Hot Posts': hot_posts, 'Rising Posts': rising_posts}

def get_my_subreddits(api):
    my_subreddits = []
    for sub in api.user.subreddits(limit=None):
        is_banned = False
        try:
            # Attempt to fetch subreddit details. This will throw a Forbidden exception if the user is banned.
            api.subreddit(sub.display_name).subscribers
        except praw.exceptions.Forbidden:
            is_banned = True
        my_subreddits.append({
            'name': sub.display_name,
            'is_banned': is_banned
        })
    return my_subreddits

def join_subreddit(api, subreddit_name):
    subreddit = api.subreddit(subreddit_name)
    subreddit.subscribe()
    return f"Successfully joined {subreddit_name}"