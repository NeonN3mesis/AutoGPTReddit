# AutoGPTReddit

Reddit API integrations using PRAW.

## Available Commands

- **fetch_comments**: Fetch comments from a post along with IDs and other metadata.
- **vote**: Vote on a post or comment.
- **fetch_notifications**: Fetch unread notifications.
- **post_comment**: Post a comment.
- **message**: Send a message response.
- **subscribe_subreddit**: Subscribe to a subreddit.
- **get_subscribed_subreddits**: Get a list of subscribed subreddits.
- **get_subreddit_info**: Fetch information about a specific subreddit.
- **get_popular_subreddits**: Fetch a list of popular subreddits.
- **read_notification**: Read a specific single full notification.
- **fetch_user_profile**: Fetches relevant information from a user's profile.
- **search_posts**: Search for posts based on a query.
- **search_comments**: Search for comments based on a query.
- **delete_item**: Delete a post or comment.

### Requires a Scenex API (Not available without API)
- **fetch_and_describe_image_post**: Fetch an image post and describe the image using SceneXplain.

## How to use a plugin

1. **Clone the plugin repo** into the Auto-GPT's plugins folder.
2. **Update your plugins_config.yaml file** to enable the plugin. If you skip this step, the plugin won't be loaded.

    ```shell
    AutoGPTReddit:
      config: {}
      enabled: true
    ```

3. **Add Reddit API Credentials to your .env**:

    ```shell
    ################################################################################
    ### REDDIT API
    ################################################################################
    # Client ID && Client Secret are found on the reddit applications portal
    REDDIT_CLIENT_ID=
    REDDIT_CLIENT_SECRET=
    REDDIT_USERNAME=
    REDDIT_USER_AGENT=
    REDDIT_PASSWORD=
    #Optional
    SCENEX_API_KEY=
    ```

## Reddit API Setup Instructions

1. **Navigate to App Preferences**: Visit the [Reddit App Preferences](https://www.reddit.com/prefs/apps/) page.
2. **Initiate App Creation**:
    - Scroll to the bottom of the "authorized applications" section.
    - Click on the link that says "are you a developer? create an app...".
3. **Configure App Details**:
    - Fill in the required fields.
    - Choose "script" as the app type.
    - Provide a redirect URI (e.g., http://localhost:8080).
    - Enter a descriptive User Agent string (e.g., "MyRedditApp/1.0").
4. **Create the App**: Click the "Create app" button.
5. **Retrieve Credentials**:
    - Find the `client_id` under the app name and copy it to `REDDIT_CLIENT_ID=`.
    - Find the `client_secret` listed as "secret" and copy it to `REDDIT_CLIENT_SECRET=`.
6. **Update Environment File**:
    - Open or create the .env file in your project directory.
    - Fill in the following lines with your details:
        - `REDDIT_CLIENT_ID=` (paste the client_id from step 5a)
        - `REDDIT_CLIENT_SECRET=` (paste the client_secret from step 5b)
        - `REDDIT_USERNAME=` (enter your Reddit username)
        - `REDDIT_USER_AGENT=` (enter the user agent string you used in step 3d)
        - `REDDIT_PASSWORD=` (enter your Reddit password)

These instructions are specifically tailored to guide you through the process of filling out the given fields for the Reddit API setup. Make sure to keep your credentials secure and follow Reddit's guidelines when choosing a user agent string.

