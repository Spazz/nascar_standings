import logging

def setup_logger(log_file="./logs/nascar.log"):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Log to both file and console
        ]
    )

    # Return a logger instance that can be used elsewhere
    return logging.getLogger()