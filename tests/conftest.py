from pathlib import Path
from trello_to_audit_report.finding_list import FindingList
import pytest

# SAMPLE_CSV_NAME = "sample_trello_export.csv"


@pytest.fixture
def findings_list():
    fl = FindingList()
    return fl
