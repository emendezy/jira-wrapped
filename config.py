#######################
# SCRIPT CONFIGURATION
#######################
DEBUG = True  # If this is True, we only pull 1 day of issues instead of 1 year
VERBOSE = False  # If this is True, we print out all the issue details
LIST_CUSTOM_FIELDS = False  # If this is True, we list all the custom fields available in the Jira instance
IMPORTANT_CUSTOM_FIELDS = [
    "Epic Link",  # Epic Link MUST come before Epic Name in this list todo: need to fix this condition
    "Epic Name",  # This will only be available on issues that are an epic
    "Story Points",
    "Dev Days"
]  # Update this with the custom fields you would like to track
