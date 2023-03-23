from trello_to_audit_report.finding_list import FindingList
import pytest

MINIMAL_CSV_FILE_NAME = "tests/test_data/minimal_export.csv"
FULL_CSV_FILE_NAME = "tests/test_data/sample_trello_export.csv"
EXPECTED_MINIMAL_RESPONSE = [
    ["hello", "hi", "hey its me"],
    ["im below hello", "im below hi ", "python is dope"],
    ["cyfrin rules", "we love cyfrin", "code"],
]


@pytest.mark.integration
def test_set_board_data_from_endpoint(integration_findings_list):
    assert len(integration_findings_list.findings_list) == 12
    assert (
        integration_findings_list.findings_list[0].title
        == "ActivePool._rebalance() does not take into account the case when the vault's strategy gets loss"
    )
    assert integration_findings_list.findings_list[0].severity == "H"
