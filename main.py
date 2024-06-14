"""https://github.com/aledade-org/intsup-poc/blame/38d417f92945a3a0b3467450bb616d45a428278e/resolve_jira_outage_issues.py#L8
Resolve Jira Outage Issues

How to create your JIRA token:
1. Go to JIRA and log in
2. Click on your profile icon in the top right corner
3. Click on "Profile"
4. Click on "Personal Access Tokens" in the left hand menu
5. Click on "Create token"
7. Enter a label and expiration date for your token and click "Create"
8. Copy the token and store it in a safe place

export JIRA_TOKEN=<your_token_here> && python main.py
"""

import os
import pdb
from typing import List, Dict, Any, Optional

from jira import JIRA, JIRAError
from datetime import datetime

#######################
# SCRIPT CONFIGURATION
#######################
DEBUG = False  # If this is True, we only pull 1 day of issues instead of 1 year
VERBOSE = False  # If this is True, we print out all the issue details
SHOW_CUSTOM_FIELD_NAMES = False
IMPORTANT_CUSTOM_FIELDS = [
    "Epic Link",  # Epic Link MUST come before Epic Name in this list todo: need to fix this condition
    "Epic Name",  # This will only be available on issues that are an epic
    "Story Points",
    "Dev Days"
]  # Update this with the custom fields you would like to track


class JiraHandler:
    def __init__(self):
        self.jira_client: JIRA = self._get_jira_client()

        # These will all be populated by the execute() method
        self.custom_fields: Optional[List] = None
        self.custom_field_map: Optional[Dict] = None
        self.issue_map: Optional[Dict] = None

        # These will be lazy loaded ie as we encounter them, map them
        self.existing_epic_map: Dict = {}

    def _get_jira_client(self) -> JIRA:
        # Jira connection details
        JIRA_SERVER = "https://jira.aledade.com"
        JIRA_BEARER_TOKEN = os.environ.get("JIRA_TOKEN")
        if not JIRA_BEARER_TOKEN:
            print("See file doc string on how to create your own jira token")
            raise ValueError("JIRA_TOKEN environment variable not set")

        options = {
            "server": JIRA_SERVER,
            "token_auth": JIRA_BEARER_TOKEN,
        }
        return JIRA(**options)

    def get_custom_fields_available(self) -> List:
        # Fetch all fields available in the JIRA instance
        try:
            fields = self.jira_client.fields()
        except JIRAError as e:
            print(f"Failed to fetch fields")
            raise e

        # Filter custom fields and display their names and IDs
        custom_fields = [field for field in fields if field["custom"]]
        if DEBUG:
            print("Number of Custom Fields: {}".format(len(custom_fields)))
        return custom_fields

    def get_custom_field_map(self) -> Dict:
        custom_field_map = {}  # This will only track fields defined in IMPORTANT_CUSTOM_FIELDS
        for field in self.custom_fields:
            if SHOW_CUSTOM_FIELD_NAMES:
                print("Custom Field ID: {}, Name: {}".format(field["id"], field["name"]))
            else:
                if field["name"] in IMPORTANT_CUSTOM_FIELDS:
                    custom_field_map[field["name"]] = field["id"]

        if len(custom_field_map) != len(IMPORTANT_CUSTOM_FIELDS):
            raise ValueError(
                "Some custom fields were not found in JIRA, "
                "please enable SHOW_CUSTOM_FIELD_NAMES to see all custom fields available."
            )
        return custom_field_map

    def generate_issue_map(self) -> Dict[str, Dict[str, Any]]:
        # get the past date as anchor for how far back we want to go
        anchor_date = (
            datetime.now().date().replace(day=datetime.now().day - 5)
            if DEBUG
            else datetime.now().date().replace(year=datetime.now().year - 1)
        )
        past_anchor = False
        start_index = 0
        max_issues_pulled_at_a_time = 50
        issue_map = {}
        while not past_anchor:
            # JQL queries
            custom_jql_query = "project in (ARCH, KG) AND assignee = emendez AND status = Done ORDER BY resolved DESC"
            issues = self.jira_client.search_issues(
                custom_jql_query,
                maxResults=max_issues_pulled_at_a_time,
                startAt=start_index
            )

            for issue in issues:
                issue_resolution_date = datetime.fromisoformat(issue.fields.resolutiondate).date()
                if issue_resolution_date < anchor_date:
                    past_anchor = True
                    break
                issue_key = issue.key
                issue_title = issue.fields.summary
                issue_description = issue.fields.description
                issue_map[issue_key] = {
                    "Title": issue_title,
                    "Description": issue_description,
                    "Resolution Date": issue_resolution_date
                }
                for custom_field_name, custom_field_id in self.custom_field_map.items():
                    if custom_field_name == "Epic Name":
                        epic_link_custom_field_id = self.custom_field_map["Epic Link"]
                        epic_link_value = (
                            getattr(issue.fields, epic_link_custom_field_id)
                            if hasattr(issue.fields, epic_link_custom_field_id)
                            else "None"
                        )
                        custom_field_value = self.get_epic_name(epic_link_value)
                    else:
                        custom_field_value = (
                            getattr(issue.fields, custom_field_id)
                            if hasattr(issue.fields, custom_field_id)
                            else "N/A"
                        )
                    issue_map[issue_key][custom_field_name] = custom_field_value
            start_index += max_issues_pulled_at_a_time
        return issue_map

    def print_issue_summary(self):
        if VERBOSE:
            for issue_key, issue_dict in self.issue_map.items():
                print("Issue Key: {}".format(issue_key))
                for field_name, field_value in issue_dict.items():
                    print("----------------")
                    print(f"{field_name}: {field_value}")
                print("===================================================================")

        # Epic summary
        epic_values = [
            f"\t{idx + 1}. {epic_name}\n"
            for idx, epic_name
            in enumerate(self.existing_epic_map.values())
       ]
        print("Epics Completed: {}".format(len(epic_values)))
        print("".join(epic_values))
        # Issue count
        issue_keys = self.issue_map.keys()
        print("Issues Completed: {}".format(len(issue_keys)))

        print("That's a wrap!")

    def get_epic_name(self, epic_link_value: str):
        """
        Lazy loader for epic names. Fetches the epic name for a given epic key.
        epic_link_value: str - The epic key ex 'ARCH-1234'
        """
        # Bailout if the epic name field is not in the custom field map
        if "Epic Name" not in self.custom_field_map:
            raise NotImplementedError(
                "'Epic Name' field not found in custom field map. Please add it to the IMPORTANT_CUSTOM_FIELDS list."
                "NOTE: 'Epic Name' should come after 'Epic Link' in the IMPORTANT_CUSTOM_FIELDS list."
            )
        if not epic_link_value or epic_link_value == "None":
            return "N/A"
        if epic_link_value not in self.existing_epic_map:
            try:
                epic_issue = self.jira_client.issue(epic_link_value)
                epic_custom_field_id = self.custom_field_map["Epic Name"]
                self.existing_epic_map[epic_link_value] = (
                    getattr(epic_issue.fields, epic_custom_field_id)
                    if hasattr(epic_issue.fields, epic_custom_field_id)
                    else "N/A"
                )
            except JIRAError as e:
                print(f"Failed to fetch epic name for {epic_link_value}. Error: {e}")

        return self.existing_epic_map[epic_link_value]

    def execute(self):
        # Get all names of custom field keys available in your JIRA instance
        self.custom_fields: List = self.get_custom_fields_available()

        # Get the custom field map for the fields you are interested in
        #  (change IMPORTANT_CUSTOM_FIELDS to include your fields of interest)
        self.custom_field_map: Dict = self.get_custom_field_map()

        # Generate a map of issues with the fields you are interested in
        self.issue_map = self.generate_issue_map()

        # Print out the issue summary with the option of being verbose and listing all issue details collected
        self.print_issue_summary()


def main():
    jira_handler = JiraHandler()
    jira_handler.execute()


if __name__ == "__main__":
    main()