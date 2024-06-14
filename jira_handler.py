"""
JIRA API wrapper handler to pull issues and summarize them
"""

import os
from typing import List, Dict, Any, Optional

from jira import JIRA, JIRAError
from datetime import datetime, timedelta

import config as cfg
from logging_utils import get_logger

logger = get_logger(__name__)


class JiraHandler:
    """Wrapper class to handle JIRA API calls and generate a summary of issues for a given user."""
    def __init__(self):
        """Initialize the JiraHandler class. Connect to JIRA and set up the logger."""
        self.jira_client: JIRA = self._get_jira_client()

        # logger that is responsible for generating the issue-details.txt file
        self.issue_detail_logger = get_logger("issue-details", stream_to_file=True)

        # Set the anchor date for how far back you want to go for your wrapped
        self.anchor_date = (datetime.now().date() - timedelta(days=cfg.WRAPPED_TIMELINE))

        # These will all be populated by the execute() method
        self.custom_fields: Optional[List] = None
        self.custom_field_map: Optional[Dict] = None
        self.issue_map: Optional[Dict] = None

        # These will be lazy loaded ie as we encounter them, map them
        self.existing_epic_map: Dict = {}

    def _get_jira_client(self) -> JIRA:
        """Connect to JIRA using the JIRA API library and return the client object."""
        jira_server = "https://jira.aledade.com"
        jira_bearer_token = os.environ.get("JIRA_TOKEN")
        if not jira_bearer_token:
            logger.error("See file doc string on how to create your own jira token")
            raise ValueError("JIRA_TOKEN environment variable not set")

        options = {
            "server": jira_server,
            "token_auth": jira_bearer_token,
        }
        return JIRA(**options)

    def get_custom_fields_available(self) -> List:
        """
        Fetch all fields available in the JIRA instance
        NOTE: Most of the fields on our tickets are custom fields
        """
        try:
            fields = self.jira_client.fields()
        except JIRAError as e:
            logger.error("Failed to fetch fields")
            raise e

        # Filter custom fields and display their names and IDs
        custom_fields = [field for field in fields if field["custom"]]
        logger.debug("Number of Custom Fields: {}".format(len(custom_fields)))
        return custom_fields

    def get_custom_field_map(self) -> Dict:
        """
        Generate the custom field map for the fields you are interested in.
        This will only track fields defined in IMPORTANT_CUSTOM_FIELDS

        will look like: {"Epic Name": "customfield_12345", "Story Points": "customfield_67890"}
        """
        custom_field_map = {}  # This will only track fields defined in IMPORTANT_CUSTOM_FIELDS
        for field in self.custom_fields:
            if cfg.LIST_CUSTOM_FIELDS:
                logger.info("Custom Field ID: {}, Name: {}".format(field["id"], field["name"]))
            else:
                if field["name"] in cfg.IMPORTANT_CUSTOM_FIELDS:
                    custom_field_map[field["name"]] = field["id"]

        if len(custom_field_map) != len(cfg.IMPORTANT_CUSTOM_FIELDS):
            raise ValueError(
                "Some custom fields were not found in JIRA, "
                "please enable DEBUG to see all custom fields available."
            )
        return custom_field_map

    def generate_issue_map(self) -> Dict[str, Dict[str, Any]]:
        """This will generate a summary of the issues for your jira wrapped.
        This returns a map of issues with the ticket number as the key
        and the fields you are interested in as the dict value."""
        # get the past date as anchor for how far back we want to go
        past_anchor = False
        start_index = 0
        max_issues_pulled_at_a_time = 50
        issue_map = {}
        while not past_anchor:
            # JQL queries
            custom_jql_query = f"project in ({cfg.PROJECT_FILTER}) AND assignee = {cfg.WHOAMI} AND status = Done ORDER BY resolved DESC"
            issues = self.jira_client.search_issues(
                custom_jql_query,
                maxResults=max_issues_pulled_at_a_time,
                startAt=start_index
            )

            for issue in issues:
                issue_resolution_date = datetime.fromisoformat(issue.fields.resolutiondate).date()
                if issue_resolution_date < self.anchor_date:
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
        """Print out the issue summary with the option of being verbose
        and generating a file of all issue details collected."""
        if cfg.VERBOSE:
            for issue_key, issue_dict in self.issue_map.items():
                self.issue_detail_logger.info("Issue Key: {}".format(issue_key))
                for field_name, field_value in issue_dict.items():
                    self.issue_detail_logger.info("-" * cfg.FILE_LOG_LINE_LENGTH)
                    self.issue_detail_logger.info("{}: {}".format(field_name, field_value))
                self.issue_detail_logger.info("=" * cfg.FILE_LOG_LINE_LENGTH)
                self.issue_detail_logger.info("\n")

        # Epic summary
        epic_values = [
            f"\t{idx + 1}. {epic_name}\n"
            for idx, epic_name
            in enumerate(self.existing_epic_map.values())
       ]
        logger.info("Epics Participated In: {}".format(len(epic_values)))
        logger.info("\n{}".format("".join(epic_values)))
        # Issue count
        issue_keys = self.issue_map.keys()
        logger.info("Issues Completed: {}".format(len(issue_keys)))
        if cfg.VERBOSE:
            logger.info("\tIssue Details are available in {}-issue-details.txt".format(cfg.WHOAMI))
        logger.info("That's a wrap!")

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
                error_msg = f"Failed to fetch epic name for {epic_link_value}. Error: {e}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        return self.existing_epic_map[epic_link_value]

    def execute(self):
        """Executor method to generate the Jira Wrapped Summary."""
        logger.info("Generating Jira Wrapped for {}...".format(cfg.WHOAMI))
        # Get all names of custom field keys available in your JIRA instance
        self.custom_fields: List = self.get_custom_fields_available()

        # Get the custom field map for the fields you are interested in
        #  (change IMPORTANT_CUSTOM_FIELDS to include your fields of interest)
        self.custom_field_map: Dict = self.get_custom_field_map()

        # Generate a map of issues with the fields you are interested in
        self.issue_map = self.generate_issue_map()

        # Print out the issue summary with the option of being verbose and listing all issue details collected
        self.print_issue_summary()
