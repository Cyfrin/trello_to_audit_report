from .finding import Finding
from typing import List
import csv
import sys
import logging as log
import requests
import os
import re

log.basicConfig(level=log.INFO)


OUTPUT_FILE_DEFAULT_NAME = "output.md"

FINDINGS_SUMMARY_HEADER = """
| Finding                                                                                                 | Severity | Status   |
| :-------------------------------------------------------------------------------------------------------| :------- | :------- |
"""

SEVERITY_ORDER = {"H": 1, "M": 2, "L": 3, "Q": 4, "G": 5}

GET_LISTS_FROM_A_BOARD_URL = "https://api.trello.com/1/boards/{}/lists?key={}&token={}"
GET_CARDS_IN_A_LIST_URL = "https://api.trello.com/1/lists/{}/cards?key={}&token={}"
GET_ATTACHMENTS_FROM_A_CARD_URL = (
    "https://api.trello.com/1/cards/{}/attachments?key={}&token={}"
)
DOWNLOAD_ATTACHMENT_FROM_A_CARD_URL = (
    "https://api.trello.com/1/cards/{}/attachments/{}/download/{}"
)
CARD_REPORT_NAME = "report.md"

TRELLO_API_KEY_ENVIRONMENT_VAR = "TRELLO_API_KEY"
TRELLO_API_TOKEN_ENVIRONMENT_VAR = "TRELLO_API_TOKEN"


class FindingList:
    def __init__(
        self,
        csv_file_or_board_id: str = "",
        attachment_name: str = None,
        api_key: str = None,
        token: str = None,
    ):
        """A finding in an audit report"""
        self.api_key = (
            os.getenv(TRELLO_API_KEY_ENVIRONMENT_VAR) if not api_key else api_key
        )
        self.token = os.getenv(TRELLO_API_TOKEN_ENVIRONMENT_VAR) if not token else token
        self._validate_args(
            csv_file_or_board_id, attachment_name, self.api_key, self.token
        )
        self.csv_file_or_board_id = csv_file_or_board_id
        self.attachment_name = attachment_name
        self.report_list_id = None

        if csv_file_or_board_id:
            if ".csv" not in csv_file_or_board_id:
                self.set_board_data_from_endpoint()
            else:
                self.findings_list: List[
                    Finding
                ] = self.generate_markdown_findings_list_from_csv(csv_file_or_board_id)
            self.sort_findings_list()
            self.summary_report: str = self.create_summary_report()

    def __str__(self):
        for finding in self.findings_list:
            print(finding + "\n")

    def get_board_id_from_endpoint(self) -> str:
        return self.csv_file_or_board_id.split("/")[-1]

    @staticmethod
    def _validate_args(
        csv_file_or_board_id: str,
        use_attachment_name_for_report: str,
        api_key: str,
        token: str,
    ):
        if ".csv" not in csv_file_or_board_id:
            if not api_key:
                log.error("You must provide an API key to use a board ID")
                sys.exit(1)
            if not token:
                log.error("You must provide a token to use a board ID")
                sys.exit(1)
        if use_attachment_name_for_report:
            if not api_key:
                log.error("You must provide an API key to use attachments")
                sys.exit(1)
            if not token:
                log.error("You must provide a token to use attachments")
                sys.exit(1)

    def set_findings_list_from_csv(self, csv_file: str):
        self.findings_list = self.generate_markdown_findings_list_from_csv(csv_file)

    def generate_markdown_findings_list_from_csv(self, csv_file: str) -> List[Finding]:
        rows = self.read_csv(csv_file)
        filtered_rows = self.get_filtered_rows(rows)

        (
            _,
            _,
            finding_description_index,
            finding_severity_index,
            finding_title_index,
        ) = self.get_header_indexes_from_header_row(rows[0])

        findings_list = []
        severity_counter = {}

        for filtered_row in filtered_rows:
            markdown_finding = self.create_finding_from_filtered_row(
                filtered_row,
                finding_description_index,
                finding_severity_index,
                finding_title_index,
            )
            severity_counter[markdown_finding.severity] = (
                severity_counter.get(markdown_finding.severity, 0) + 1
            )
            markdown_finding.number = severity_counter[markdown_finding.severity]
            findings_list.append(markdown_finding)
        return findings_list

    @staticmethod
    def custom_sort_key(finding: Finding):
        return (SEVERITY_ORDER.get(finding.severity, 6), finding.number)

    def get_sorted_findings_list(self, findings_list: List[Finding]) -> List[Finding]:
        return sorted(findings_list, key=self.custom_sort_key)

    def sort_findings_list(self):
        self.findings_list = self.get_sorted_findings_list(self.findings_list)

    def read_csv(self, csv_file: str) -> List[str]:
        rows = []
        with open(csv_file, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                rows.append(row)
        return rows

    def get_header_indexes_from_header_row(self, row: List[str]) -> dict:
        lowercase_row_headers = [s.lower() for s in row]
        list_name_index = lowercase_row_headers.index("list name")
        archived_index = lowercase_row_headers.index("archived")
        finding_description_index = lowercase_row_headers.index("card description")
        finding_severity_index = lowercase_row_headers.index("labels")
        finding_title_index = lowercase_row_headers.index("card name")
        return (
            list_name_index,
            archived_index,
            finding_description_index,
            finding_severity_index,
            finding_title_index,
        )

    def get_filtered_rows(self, rows: List[str]) -> List[str]:
        (
            list_name_index,
            archived_index,
            _,
            _,
            _,
        ) = self.get_header_indexes_from_header_row(rows[0])

        # Filter columns by 'List Name' and 'Archived'
        filtered_rows = [
            row
            for row in rows
            if row[list_name_index] == "Report" and (row[archived_index] != "true")
        ]
        return filtered_rows

    def create_finding_from_filtered_row(
        self,
        filtered_row: List[str],
        finding_description_index: int,
        finding_severity_index: int,
        finding_title_index: int,
    ) -> Finding:
        """
        Create a markdown finding string from a row of the csv file.
        """
        formatted_severity = filtered_row[finding_severity_index].split(" ")[0][0]
        return Finding(
            description=filtered_row[finding_description_index],
            severity=formatted_severity,
            title=filtered_row[finding_title_index],
        )

    def print_findings_list(self) -> None:
        for finding in self.findings_list:
            print(finding)

    def save_to_output_file(
        self, output_file: str = None, text_before: str = ""
    ) -> None:
        if not output_file:
            output_file = OUTPUT_FILE_DEFAULT_NAME
        with open(output_file, "w") as f:
            f.write(text_before)
            f.write(self.summary_report)
            for finding in self.findings_list:
                f.write(str(finding) + "\n")

    def create_summary_report(self) -> str:
        """Create a summary of the findings in the audit report"""
        summary_report = FINDINGS_SUMMARY_HEADER
        self.sort_findings_list()

        for finding in self.findings_list:
            finding_summary_title = finding.get_summary_title()
            summary_report += (
                "| ["
                + finding_summary_title
                + "]("
                + finding.get_summary_title_hyperlink()
                + ") |"
                + finding.severity
                + "| Open |\n"
            )
        return summary_report

    def set_findings_summary(self):
        self.summary_report = self.create_summary_report()

    def set_board_data_from_endpoint(self):
        lists_from_board_request_response = requests.get(
            GET_LISTS_FROM_A_BOARD_URL.format(
                self.csv_file_or_board_id, self.api_key, self.token
            )
        )
        list_of_lists = lists_from_board_request_response.json()
        for list in list_of_lists:
            if list["name"].lower() == "report":
                self.report_list_id = list["id"]
        if not self.report_list_id:
            log.error(
                f"Could not find a list named 'Report' in the board with id {self.csv_file_or_board_id}"
            )
            sys.exit(1)

        cards_from_list_response = requests.get(
            GET_CARDS_IN_A_LIST_URL.format(
                self.report_list_id, self.api_key, self.token
            )
        )
        cards_from_list_data = cards_from_list_response.json()
        self.findings_list = []
        for card in cards_from_list_data:
            finding = Finding(
                description=card["desc"],
                severity=card["labels"][0]["name"][0],
                title=card["name"],
                id=card["id"],
                url=card["url"],
            )
            finding.attachment_id = self.get_attachment_id_using_card_id(finding.id)
            finding.description = self.download_attachment(
                finding.id, finding.attachment_id, url=finding.url
            )
            self.findings_list.append(finding)

    def get_attachment_id_using_card_id(self, card_id: str):
        attachments_from_card_response = requests.get(
            GET_ATTACHMENTS_FROM_A_CARD_URL.format(card_id, self.api_key, self.token)
        )
        attachments_from_card_data = attachments_from_card_response.json()
        for attachment in attachments_from_card_data:
            if attachment["name"] == CARD_REPORT_NAME:
                return attachment["id"]
        if len(attachments_from_card_data) > 0:
            return attachments_from_card_data[0]["id"]
        return None

    def download_attachment(
        self, card_id: str, attachment_id: str, url: str = None
    ) -> str:
        # "Authorization: OAuth oauth_consumer_key=\"{{key}}\", oauth_token=\"{{token}}\""
        headers = {
            "Authorization": f'OAuth oauth_consumer_key="{self.api_key}", oauth_token="{self.token}"'
        }
        response = requests.get(
            DOWNLOAD_ATTACHMENT_FROM_A_CARD_URL.format(
                card_id, attachment_id, CARD_REPORT_NAME
            ),
            headers=headers,
        )
        if response.status_code >= 200 and response.status_code <= 299:
            return response.text
        if url:
            return f"Error getting attachment.\nPlease name the attachment to {CARD_REPORT_NAME}. The erroring Card ID:\n\t{card_id}\nURL:\n\t{url}."
        return f'Error getting attachment.\nPlease name the attachment to "{CARD_REPORT_NAME}". The erroring Card ID:\n\t{card_id}. URL not provided.'
