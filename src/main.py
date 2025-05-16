# maestro-log-analysis/src/main.py

import os
import glob
import logging
from log_parser import LogParser
from utils.sftp import download_logs_from_sftp, read_sftp_config
from utils.db import save_inbound_transfers_to_duckdb  # Import the DuckDB utility
from utils.logging_config import configure_logging # Import the logging configuration

# Configure logging
configure_logging()

def main():
    try:
        # Set up the logging configuration
        logging.info("Starting log analysis tool...")
        # Check log files source
        source_log_from_sftp = os.getenv("LOGS_SOURCE", "sftp").lower() == "true"
        local_path = "data"  # Default local path for log files

        if source_log_from_sftp:
            # Read SFTP configuration
            sftp_host, sftp_username, sftp_password, remote_path, local_path = read_sftp_config()

            # Download log files from SFTP
            logging.info("Downloading log files from SFTP...")
            download_logs_from_sftp(sftp_host, sftp_username, sftp_password, remote_path, local_path)
        else:
            logging.info("Sourcing logs from local FS.")

        # Process log files
        log_file_pattern = os.path.join(local_path, 'Inbound_*.log')  # Pattern to match all log files
        log_files = glob.glob(log_file_pattern)  # Find all matching log files

        if not log_files:
            logging.warning(f"No log files found matching pattern: {log_file_pattern}")
            return

        parser = LogParser()
        all_inbound_transfers = []

        for log_file_path in log_files:
            logging.info(f"Processing log file: {log_file_path}")
            inbound_transfers = parser.parse_log_file(log_file_path)
            all_inbound_transfers.extend(inbound_transfers)

        # Save the results to a DuckDB database
        logging.info("Saving results to DuckDB database...")
        save_inbound_transfers_to_duckdb(all_inbound_transfers)
        logging.info("Log analysis completed successfully.")

    except Exception as e:
        logging.error(f"Error processing log files {log_file_path}: {e}")

if __name__ == "__main__":
    main()