import logging
import os
import csv

# Ensure logs directory exists
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)

# File paths
log_file_path = os.path.join(log_directory, "app.log")
csv_log_file_path = os.path.join(log_directory, "app.csv")

# Set up logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

# Formatter for logs
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Stream handler (Console Output)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# File handler (Standard Log File)
file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)

# CSV Formatter (Custom for CSV Output)
class CSVFormatter(logging.Formatter):
    """Custom CSV log formatter."""
    def format(self, record):
        log_time = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        return f"{log_time},{record.levelname},{record.message}"

# File handler for CSV logs
csv_handler = logging.FileHandler(csv_log_file_path, mode="a", encoding="utf-8")
csv_handler.setFormatter(CSVFormatter())

# Add handlers to logger
logger.addHandler(stream_handler)  # Console
logger.addHandler(file_handler)    # Standard log file
logger.addHandler(csv_handler)     # CSV log file

# Write CSV header only if the file is empty
if not os.path.exists(csv_log_file_path) or os.stat(csv_log_file_path).st_size == 0:
    with open(csv_log_file_path, mode="w", newline="", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Timestamp", "Log Level", "Message"])  # CSV headers
