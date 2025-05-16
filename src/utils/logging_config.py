import logging
from logging.handlers import RotatingFileHandler

def configure_logging(log_file="log_analysis_tool.log", max_bytes=10 * 1024 * 1024, backup_count=5):
    """Configure logging with rolling log files."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count),  # Rolling log files
            logging.StreamHandler()  # Log to the console
        ]
    )