"""Configuration file for the Jira Wrapped script."""
import os
from typing import Union
from dotenv import load_dotenv

load_dotenv()


def str2bool(boolstring: Union[str, bool]) -> bool:
    if type(boolstring) is bool:
        return boolstring
    return boolstring.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'alright', 'okay']


#######################
# SCRIPT CONFIGURATION
#######################
DEBUG = str2bool(os.environ.get("DEBUG", True))  # If this is True, we only pull 1 day of issues instead of 1 year
VERBOSE = str2bool(os.environ.get("VERBOSE", True))  # If this is True, we print out all the issue details
LIST_CUSTOM_FIELDS = str2bool(os.environ.get("LIST_CUSTOM_FIELDS", False))  # If this is True, we list all the custom fields available in the Jira instance
FILE_LOG_LINE_LENGTH = int(os.environ.get("FILE_LOG_LINE_LENGTH", 120))  # Max length of the lines that the logs wrap to
WRAPPED_TIMELINE = int(os.environ.get("WRAPPED_TIMELINE", 5))  # Number of days to pull issues for our jira wrapped summary
WHOAMI = os.environ.get("WHOAMI", "your jira username")  # Jira wrapped will use this account

PROJECT_FILTER = "ARCH, KG"  # This is the project filter for the Jira query
IMPORTANT_CUSTOM_FIELDS = [
    "Epic Link",  # Epic Link MUST come before Epic Name in this list todo: need to fix this condition
    "Epic Name",  # This will only be available on issues that are an epic
    "Story Points",
    "Dev Days"
]  # Update this with the custom fields you would like to track
