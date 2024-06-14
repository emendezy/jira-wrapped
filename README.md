# JIRA Wrapped
Author: Eric Mendez

## How to create your JIRA token:
1. Go to JIRA and log in
2. Click on your profile icon in the top right corner
3. Click on "Profile"
4. Click on "Personal Access Tokens" in the left hand menu
5. Click on "Create token"
7. Enter a label and expiration date for your token and click "Create"
8. Copy the token and store it in a safe place

## Setup your local environment
0. Install pyenv and the python version 3.11.5
```bash
brew install pyenv
pyenv install 3.11.5
```
1. Create a virtual environment
```bash
pyenv virtualenv 3.11.5 jira-wrapped
```
2. Activate the virtual environment
```bash
pyenv activate jira-wrapped
```
3. Install the dependencies
```bash
pip install -r requirements.txt
```
4. Ensure you have all the requirements installed with the following command
```bash
pip freeze # should look like the requirements.txt file
```

## Script configurations
1. Go to the config.py file and see what configs are available to change
2. Create your own .env file that overrides the default configurations to your preference

## How to run this script
```bash
python get_jira_wrapped.py
```

## Recommendations
1. Start with these configurations in your .env file:
```bash
DEBUG=True
VERBOSE=True
LIST_CUSTOM_FIELDS=True
FILE_LOG_LINE_LENGTH=120
JIRA_TOKEN=<you need to fill this in>
WHOAMI=<your username in jira>
WRAPPED_TIMELINE=5 # days
```
2. Change the configs for IMPORTANT_CUSTOM_FIELDS and PROJECT_FILTER to your preference
- `PROJECT_FILTER` is a list of project key prefixes that you want to filter on (ex ['ARCH', 'KG'])
- `IMPORTANT_CUSTOM_FIELDS` is a list of custom fields that you want to see in the output (ex ['Labels', 'Subteam'])
  - If you don't know what custom fields are available, set `LIST_CUSTOM_FIELDS` to True and run the script
  - NOTE -- Most of the jira fields are custom fields
  - Their names are normally the same as you would see on a ticket in JIRA ie "Epic Link"
3. Run the script and see what the output looks like
4. Once you are happy with the output, you can change the `DEBUG` flag to False and increase the `WRAPPED_TIMELINE` to a larger number, I recommend 365 days for that year long view
5. Run the script again and see YOUR JIRA WRAPPED! :sunglasses:
