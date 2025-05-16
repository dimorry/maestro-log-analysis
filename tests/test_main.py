import os
import pytest
from unittest.mock import patch, MagicMock
from main import main
from log_parser import LogParser
from utils.db import save_inbound_transfers_to_duckdb
from utils.sftp import download_logs_from_sftp

@pytest.fixture
def mock_env_sftp(monkeypatch):
    """Set the environment variable LOGS_SOURCE to 'sftp'."""
    monkeypatch.setenv("LOGS_SOURCE", "sftp")

@pytest.fixture
def mock_env_local(monkeypatch):
    """Set the environment variable LOGS_SOURCE to 'local'."""
    monkeypatch.setenv("LOGS_SOURCE", "local")

@patch("main.download_logs_from_sftp")
@patch("main.glob.glob")
@patch("main.LogParser")
@patch("main.save_inbound_transfers_to_duckdb")
def test_sftp_file_processing(mock_save_db, mock_log_parser, mock_glob, mock_download_sftp, mock_env_sftp):
    """Test processing files from SFTP."""
    # Mock SFTP download
    mock_download_sftp.return_value = None

    # Mock glob to return a list of files
    mock_glob.return_value = ["file1.log", "file2.log"]

    # Mock LogParser to return parsed data
    mock_parser_instance = MagicMock()
    mock_parser_instance.parse_log_file.return_value = [{"filename": "file1.log", "size": 100}]
    mock_log_parser.return_value = mock_parser_instance

    # Run the main function
    main()

    # Assert SFTP download was called
    mock_download_sftp.assert_called_once()

    # Assert files were processed
    mock_parser_instance.parse_log_file.assert_any_call("file1.log")
    mock_parser_instance.parse_log_file.assert_any_call("file2.log")

    # Assert data was saved to the database
    mock_save_db.assert_called_once_with([{"filename": "file1.log", "size": 100}])

@patch("main.glob.glob")
@patch("main.LogParser")
@patch("main.save_inbound_transfers_to_duckdb")
def test_local_file_processing(mock_save_db, mock_log_parser, mock_glob, mock_env_local):
    """Test processing files from local filesystem."""
    # Mock glob to return a list of files
    mock_glob.return_value = ["file1.log", "file2.log"]

    # Mock LogParser to return parsed data
    mock_parser_instance = MagicMock()
    mock_parser_instance.parse_log_file.return_value = [{"filename": "file1.log", "size": 100}]
    mock_log_parser.return_value = mock_parser_instance

    # Run the main function
    main()

    # Assert SFTP download was not called
    # Assert files were processed
    mock_parser_instance.parse_log_file.assert_any_call("file1.log")
    mock_parser_instance.parse_log_file.assert_any_call("file2.log")

    # Assert data was saved to the database
    mock_save_db.assert_called_once_with([{"filename": "file1.log", "size": 100}])

@patch("main.logging.error")
@patch("main.LogParser")
def test_error_handling(mock_log_parser, mock_logging_error, mock_env_local):
    """Test error handling during file processing."""
    # Mock LogParser to raise an exception
    mock_parser_instance = MagicMock()
    mock_parser_instance.parse_log_file.side_effect = Exception("Parsing error")
    mock_log_parser.return_value = mock_parser_instance

    # Run the main function
    main()

    # Assert error was logged
    mock_logging_error.assert_called_with("Error processing log files file1.log: Parsing error")