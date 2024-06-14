# JIRA Wrapped

## How to create your JIRA token:
1. Go to JIRA and log in
2. Click on your profile icon in the top right corner
3. Click on "Profile"
4. Click on "Personal Access Tokens" in the left hand menu
5. Click on "Create token"
7. Enter a label and expiration date for your token and click "Create"
8. Copy the token and store it in a safe place

## Script configurations
Go to the config.py file and set the following script configs:
- DEBUG -- (True) Pulls smaller data sets for testing and shows more detailed messages
- VERBOSE = (True) Print out all every issue's details that we've collected
- LIST_CUSTOM_FIELDS = (True) List all the custom fields available in the Jira instance
- IMPORTANT_CUSTOM_FIELDS -- (List[str]) Update this with your JIRA custom fields you would like to track

## How to run this script
```bash
export JIRA_TOKEN=<your_token_here> && python main.py
```
