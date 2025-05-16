import re
import logging
from datetime import datetime
import pytz  # Import pytz for timezone handling

class LogParser:
    def parse_log_file(self, log_file_path):
        transfers = []
        with open(log_file_path, 'r') as log_file:
            lines = log_file.readlines()

        for line_number, line in enumerate(lines, start=1):  # Add line numbers
            try:
                if "Transfer of file" in line:
                    if "is about to start" in line:
                        # Extract start details
                        transfer_data = self._parse_start_line(line)
                        transfer_data['action'] = "InboundTransfer"  # Add action column
                        transfer_data['start_line_number'] = line_number  # Add line number column
                    elif "is complete" in line:
                        # Extract completion details
                        completed_data = self._parse_complete_line(line)
                        completed_data['end_line_number'] = line_number  # Add line number column
                        transfer_data.update(completed_data)
                        # Calculate transfer rate
                        transfer_data['rate'] = self._calculate_transfer_rate(
                            transfer_data['size'], transfer_data['duration']
                        )
                    transfers.append(transfer_data)
            except Exception as e:
                logging.error(f"Error parsing line {line_number}: {line.strip()} - {e}")

                # Clean up to ensure no invalid data is appended
                transfer_data["filename"] = f"Error parsing line {line_number}: {line.strip()} - {e}"

                continue  # Skip to the next line on error
        return transfers

    def _parse_start_line(self, line):
        # Use regex to extract timestamp, filename, and size from the start line
        # Example: INFO 2024-12-04 11:00:36,713  InboundMonitor_ - Transfer of file SalesOrdersChange.20241204T160022.tab is about to start. Bytes = 522.
        match = re.search(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) .* Transfer of file (.+\.tab) is about to start\. Bytes = (\d+)", line
        )
        if match:
            start_timestamp = self._convert_to_est(match.group(1))  # Convert to EST timezone
            filename = match.group(2)
            size = int(match.group(3))
            filetype = filename.split('.')[0]  # Extract the portion before the first '.'
            return {
                "filename": filename,
                "size": size,
                "rate": None,
                "duration": 0,
                "filetype": filetype,
                "end_line_number": None,  # Placeholder for end line number
                "start_timestamp": start_timestamp,
                "end_timestamp": None  # Placeholder for end timestamp
            }
        raise ValueError("Failed to parse start line")

    def _parse_complete_line(self, line):
        # Use regex to extract timestamp and duration from the completion line
        # Example: INFO 2024-12-04 11:00:36,869  InboundMonitor_ - Transfer of file SalesOrdersChange.20241204T160022.tab is complete. Bytes=0; Seconds=0.156.
        match = re.search(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) .* Transfer of file .* is complete\. .* Seconds=(\d+\.\d+)", line
        )
        if match:
            end_timestamp = self._convert_to_est(match.group(1))  # Convert to EST timezone
            duration = float(match.group(2))
            return {
                "end_timestamp": end_timestamp,
                "duration": duration
            }
        raise ValueError("Failed to parse complete line")

    def _convert_to_est(self, timestamp_str):
        """Convert a timestamp string to an EST timezone-aware datetime object."""
        naive_datetime = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")  # Parse without timezone
        est_timezone = pytz.timezone("US/Eastern")  # Define EST timezone
        return est_timezone.localize(naive_datetime)  # Localize the naive datetime to EST

    def _calculate_transfer_rate(self, size, duration):
        return size / duration if duration > 0 else 0