import logging

# Set up logger
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

# Formatter for logs
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Stream handler for console output
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# File handler for log storage
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
