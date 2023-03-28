from trello_to_audit_report.finding_list import FindingList
import pytest


INTEGRATION_TEST_CARD_ID = "ZuSC06dO"
CARD_URL = "https://trello.com/c/ZuSC06dO/9-activepoolrebalance-does-not-take-into-account-the-case-when-the-vaults-strategy-gets-loss"


@pytest.mark.integration
def test_set_board_data_from_endpoint(integration_findings_list):
    assert len(integration_findings_list.findings_list) == 4
    assert (
        integration_findings_list.findings_list[0].title
        == "ActivePool._rebalance() does not take into account the case when the vault's strategy gets loss"
    )
    assert integration_findings_list.findings_list[0].severity == "H"
    assert integration_findings_list.findings_list[0].severity == "H"


@pytest.mark.integration
def test_get_attachment_id_using_card_id(integration_findings_list):
    attachment_id: str = integration_findings_list.get_attachment_id_using_card_id(
        INTEGRATION_TEST_CARD_ID
    )
    description: str = integration_findings_list.download_attachment(
        INTEGRATION_TEST_CARD_ID, attachment_id, url=CARD_URL
    )
    assert description.startswith("ActivePool")
