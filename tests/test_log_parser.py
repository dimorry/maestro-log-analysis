import pytest
from log_parser import LogParser
from datetime import datetime
import pytz

@pytest.fixture
def log_parser():
    """Fixture to create a LogParser instance."""
    return LogParser()

def test_parse_start_line(log_parser):
    """Test parsing a start line."""
    line = "INFO 2024-12-04 11:00:36,713  InboundMonitor_ - Transfer of file SalesOrdersChange.20241204T160022.tab is about to start. Bytes = 522."
    result = log_parser._parse_start_line(line)

    est_timezone = pytz.timezone("US/Eastern")
    expected_timestamp = est_timezone.localize(datetime(2024, 12, 4, 11, 0, 36, 713000))

    assert result["filename"] == "SalesOrdersChange.20241204T160022.tab"
    assert result["size"] == 522
    assert result["filetype"] == "SalesOrdersChange"
    assert result["start_timestamp"] == expected_timestamp
    assert result["end_timestamp"] is None

def test_parse_complete_line(log_parser):
    """Test parsing a complete line."""
    line = "INFO 2024-12-04 11:00:36,869  InboundMonitor_ - Transfer of file SalesOrdersChange.20241204T160022.tab is complete. Bytes=0; Seconds=0.156."
    result = log_parser._parse_complete_line(line)

    est_timezone = pytz.timezone("US/Eastern")
    expected_timestamp = est_timezone.localize(datetime(2024, 12, 4, 11, 0, 36, 869000))

    assert result["end_timestamp"] == expected_timestamp
    assert result["duration"] == 0.156

def test_parse_log_file(log_parser, caplog):
    """Test parsing a full log file."""
    log_file_content = [
        "INFO 2024-12-04 11:00:36,713  InboundMonitor_ - Transfer of file SalesOrdersChange.20241204T160022.tab is about to start. Bytes = 522.",
        "INFO 2024-12-04 11:00:36,869  InboundMonitor_ - Transfer of file SalesOrdersChange.20241204T160022.tab is complete. Bytes=0; Seconds=0.156.",
        "INVALID LINE"
    ]

    with caplog.at_level("ERROR"):
        with pytest.raises(ValueError):
            transfers = log_parser.parse_log_file(log_file_content)

    assert len(transfers) == 1
    assert transfers[0]["filename"] == "SalesOrdersChange.20241204T160022.tab"
    assert transfers[0]["start_timestamp"] is not None