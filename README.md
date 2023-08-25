# AutoGPTReddit
Reddit API integrations using PRAW

### Available Functions
- get_posts_from_subreddit
- get_comments_on_post
- submit_post
- submit_comment_on_post
- reply_to_comment
- search_reddit
- upvote
- downvote
- search_reddit_user

### How to use a plugin

1. **Clone the plugin repo** into the Auto-GPT's plugins folder.
2. **Install the plugin's dependencies (if any): (Skip this step if you are using Docker Compose)**
   Navigate to the plugin's folder in your terminal, and run the following command to install any required dependencies:

   ```shell
   pip install -r requirements.txt
   ```
3. **Update your plugins_config.yaml file** to enable the plugin. If you skip this step, the plugin won't be loaded.
   

   ```shell
   AutoGPTReddit:
     config: {}
     enabled: true
   ```
4. **Add Reddit API Credentials to your .env**:

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
   ```

### Reddit API Setup Instructions

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
