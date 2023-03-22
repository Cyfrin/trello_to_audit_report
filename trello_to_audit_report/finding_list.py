from .finding import Finding
from typing import List
import csv

OUTPUT_FILE_DEFAULT_NAME = "output.md"

FINDINGS_SUMMARY_HEADER = """
| Finding                                                                             | Severity | Status   |
| :-----------------------------------------------------------------------------------| :------- | :------- |
"""

SEVERITY_ORDER = {"H": 1, "M": 2, "L": 3, "Q": 4, "G": 5}


class FindingList:
    def __init__(self, csv_file: str = None):
        """A finding in an audit report"""
        if csv_file:
            self.findings_list: List[
                Finding
            ] = self.generate_markdown_findings_list_from_csv(csv_file)
            self.sort_findings_list()
            self.summary_report: str = self.create_summary_report()

    def __str__(self):
        for finding in self.findings_list:
            print(finding + "\n")

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
    def custom_sort_key(finding):
        return (SEVERITY_ORDER.get(finding.severity, 6), finding.number)

    @classmethod
    def get_sorted_findings_list(self, findings_list: List[Finding]) -> List[Finding]:
        return sorted(findings_list, key=self.custom_sort_key)

    def sort_findings_list(self):
        self.findings_list = self.get_sorted_findings_list(self.findings_list)

    @classmethod
    def read_csv(self, csv_file: str) -> List[str]:
        rows = []
        with open(csv_file, "r") as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                rows.append(row)
        return rows

    @classmethod
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

    @classmethod
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

    def save_to_output_file(self, output_file: str = None) -> None:
        if not output_file:
            output_file = OUTPUT_FILE_DEFAULT_NAME
        with open(output_file, "w") as f:
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
