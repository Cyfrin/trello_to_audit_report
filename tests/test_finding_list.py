from trello_to_audit_report.finding_list import FindingList

MINIMAL_CSV_FILE_NAME = "tests/test_data/minimal_export.csv"
FULL_CSV_FILE_NAME = "tests/test_data/sample_trello_export.csv"
EXPECTED_MINIMAL_RESPONSE = [
    ["hello", "hi", "hey its me"],
    ["im below hello", "im below hi ", "python is dope"],
    ["cyfrin rules", "we love cyfrin", "code"],
]


def test_read_csv(findings_list):
    # Arrange / Act
    rows = findings_list.read_csv(MINIMAL_CSV_FILE_NAME)
    # Assert
    assert EXPECTED_MINIMAL_RESPONSE == rows


def test_filter_rows(findings_list):
    # Arrange
    rows = findings_list.read_csv(FULL_CSV_FILE_NAME)
    # Act
    filetered_rows = findings_list.get_filtered_rows(rows)
    # Assert
    assert len(filetered_rows) == 2


def test_generate_markdown_findings_list_from_csv(findings_list):
    # Arrange / Act
    markdown_findings = findings_list.generate_markdown_findings_list_from_csv(
        FULL_CSV_FILE_NAME
    )
    # Assert
    assert len(markdown_findings) == 2
    assert markdown_findings[0].number == 1
    assert markdown_findings[1].number == 1
    assert markdown_findings[0].severity == "H"
    assert markdown_findings[1].severity == "L"


def test_create_summary_report(findings_list):
    findings_list.set_findings_list_from_csv(FULL_CSV_FILE_NAME)
    summary_report = findings_list.create_summary_report()
    # TODO: Add the assert lol
