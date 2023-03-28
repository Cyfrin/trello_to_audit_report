from trello_to_audit_report.finding_list import FindingList
from trello_to_audit_report.finding import Finding

FULL_CSV_FILE_NAME = "tests/test_data/sample_export_ethos.csv"
EXPECTED_SUMMARY_TITLE_HYPERLINK = "#h-1-activepool_rebalance-does-not-take-into-account-the-case-when-the-vaults-strategy-gets-loss"

INITAL_BIG_DESCRIPTION = f"""
ActivePool.\_rebalance() does not consider the case when the vault's strategy gets loss

https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L251
https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L282
https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L288

## Impact

The \_rebalance() reverts if a strategy gets loss.
Because \_rebalance() is called on all important workflows, this leads to insolvency of the protocol.

## Proof of Concept

The protocol uses ReaperVaultERC4626 to manage the collateral assets and farm profit.
The vaults are connected to whitelisted strategies.
"""

EXPECTED_BIG_DESCRIPTION = f"""
ActivePool.\_rebalance() does not consider the case when the vault's strategy gets loss

https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L251
https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L282
https://github.com/code-423n4/2023-02-ethos/blob/73687f32b934c9d697b97745356cdf8a1f264955/Ethos-Core/contracts/ActivePool.sol#L288

### Impact

The \_rebalance() reverts if a strategy gets loss.
Because \_rebalance() is called on all important workflows, this leads to insolvency of the protocol.

### Proof of Concept

The protocol uses ReaperVaultERC4626 to manage the collateral assets and farm profit.
The vaults are connected to whitelisted strategies.
"""


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


def test_fix_markdown_headers_big():
    # Arrange
    finding = Finding(description=INITAL_BIG_DESCRIPTION)
    # Act
    finding.fix_markdown_headers()
    # Assert
    assert finding.description == EXPECTED_BIG_DESCRIPTION
