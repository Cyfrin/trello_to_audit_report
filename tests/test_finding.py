from trello_to_audit_report.finding_list import FindingList

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
