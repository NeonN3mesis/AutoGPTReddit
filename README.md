# AutoGPTReddit

Reddit API integrations using PRAW.
This plugin targets the master branch of AutoGPT currently. AutoGPT is developing rapidly and the master branch is broken often, therefore this plugin is also devopling rapidly and is also broken often. Upon the next stable release of AutoGPT, I will also release a stable branch. 

### :warning: WARNING: THIS PLUGIN ADDS SIGNIFICANT OVERHEAD TO THE PROMT AND REQUESTS SIGNIFICANT AMONTS OF DATA WHICH WILL DRASTICALLY INCREASE API USEAGE AND COST :warning:

## Available Commands

- **fetch_comments**: Fetch comments from a post along with IDs and other metadata.
- **vote**: Vote on a post or comment.
- **fetch_notifications**: Fetch unread notifications.
- **submit_comment**: Submit a comment.
- **message**: Send a message response.
- **subscribe_subreddit**: Subscribe to a subreddit.
- **get_subscribed_subreddits**: Get a list of subscribed subreddits.
- **get_subreddit_info**: Fetch information about a specific subreddit.
- **get_popular_subreddits**: Fetch a list of popular subreddits.
- **read_notification**: Read a specific single full notification.
- **fetch_user_profile**: Fetches relevant information from a user's profile.
- **search_posts**: Search for posts based on a query.
- **search_comments**: Search for comments based on a query.
- **fetch_comment_tree**: Fetch a comment and all its children comments.
- **submit_post**: Submit a post (`CAN_GENERATE_POSTS=true` in .env required)

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
    CAN_GENERATE_POSTS=false
    #(Default=false)
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



# AutoGPTReddit Plugin Legal Disclaimer

---

## :warning: WARNING: PLEASE READ THIS DISCLAIMER CAREFULLY BEFORE USING THE AUTOGPTREDDIT PLUGIN WITH AUTO-GPT :warning:

By using the AutoGPTReddit Plugin ("Plugin") with Auto-GPT ("Agent"), you acknowledge and agree to the following terms and conditions:

---

### 1. Risk of Harm

You understand that using the Plugin with your Agent to interact with Reddit or any other third-party service may cause unintended actions or consequences, including but not limited to data loss, privacy violations, and violations of Reddit's terms of service.

---

### 2. No Warranty

The Plugin is provided "AS IS" without any warranties of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement.

---

### 3. No Liability

Under no circumstances shall the developers, contributors, or anyone involved in the creation or distribution of the Plugin be liable for any damages (including, without limitation, direct, indirect, incidental, special, consequential, or exemplary damages) arising out of the use or inability to use the Plugin.

---

### 4. Indemnification

You agree to indemnify and hold harmless the developers, contributors, and anyone involved in the creation or distribution of the Plugin from and against any and all claims, liabilities, damages, and expenses (including legal fees) arising out of your use of the Plugin.

---

### 5. Compliance

It is your sole responsibility to ensure that your use of the Plugin complies with all applicable laws, including but not limited to federal, state, and local laws, as well as Reddit's terms of service.

---

By using the Plugin, you acknowledge that you have read, understood, and agree to be bound by these terms.



