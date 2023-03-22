from pathlib import Path
from trello_to_audit_report.finding_list import FindingList
import pytest


@pytest.fixture
def findings_list():
    fl = FindingList()
    return fl
