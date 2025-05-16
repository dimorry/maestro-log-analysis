def extract_filename(log_entry):
    """Extracts the filename from a log entry."""
    parts = log_entry.split(" - ")
    if len(parts) > 1:
        filename_part = parts[1]
        filename = filename_part.split(" is ")[1].split(" ")[0]
        return filename
    return None

def format_time(seconds):
    """Formats time in seconds to a more readable format."""
    return f"{seconds:.3f} seconds"

def parse_bytes(bytes_str):
    """Parses the bytes string to an integer."""
    return int(bytes_str.split("=")[-1].strip())