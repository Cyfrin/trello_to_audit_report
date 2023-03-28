from trello_to_audit_report.finding_list import FindingList
from trello_to_audit_report.finding import Finding

FULL_CSV_FILE_NAME = "tests/test_data/sample_export_ethos.csv"
EXPECTED_SUMMARY_TITLE_HYPERLINK = "#h-1-activepool_rebalance-does-not-take-into-account-the-case-when-the-vaults-strategy-gets-loss"


def test_get_summary_title_hyperlink():
    # Arrange
    fl = FindingList(FULL_CSV_FILE_NAME)
    # Act
    assert (
        EXPECTED_SUMMARY_TITLE_HYPERLINK
        == fl.findings_list[0].get_summary_title_hyperlink()
    )


def test_fix_markdown_headers():
    # Arrange
    initial_description = "# Impact \n some stuff here \n## Description \n some stuff here \n### Mitigation \n some stuff here \n#### 4 here\n asdfasdf \n# Impact 2 \n some stuff here \n## Description 2 \n some stuff here \n### Mitigation 2 \n some stuff here"
    expected_description = "### Impact \n some stuff here \n### Description \n some stuff here \n### Mitigation \n some stuff here \n#### 4 here\n asdfasdf \n### Impact 2 \n some stuff here \n### Description 2 \n some stuff here \n### Mitigation 2 \n some stuff here"
    finding = Finding(description=initial_description)
    # Act
    finding.fix_markdown_headers()
    # Assert
    assert finding.description == expected_description
