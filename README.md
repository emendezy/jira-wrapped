# JIRA Wrapped

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
