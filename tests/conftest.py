from trello_to_audit_report.finding_list import FindingList
import pytest

INTEGRATION_TEST_BOARD_ID = "1AhNmEQE"


@pytest.fixture
def findings_list():
    fl = FindingList()
    return fl


@pytest.mark.integration
@pytest.fixture
def integration_findings_list():
    fl = FindingList(INTEGRATION_TEST_BOARD_ID)
    return fl
