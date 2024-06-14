import logging
import config as cfg


class FileLoggerFormatter(logging.Formatter):
    """Custom formatter that wraps log messages to a specific length when writing to a file.
    It won't break words during wrapping"""
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        # Get the original formatted message
        msg = super().format(record)

        # Split the message into words
        words = msg.split()
        lines = []
        current_line = ""

        # Iterate through words and add them to lines respecting the wrap length
        for word in words:
            if len(current_line) + len(word) + 1 > cfg.FILE_LOG_LINE_LENGTH:  # Add 1 for the space between words
                lines.append(current_line)
                current_line = word
            elif not current_line:  # Handle the first word in the line
                current_line = word
            else:
                current_line += " " + word

        # Add the last line
        if current_line:
            lines.append(current_line)

        # Join the lines to create the wrapped message
        wrapped_msg = "\n".join(lines)
        return wrapped_msg.strip("\n")


def get_logger(name, stream_to_file=False):
    """Create a logger with the given name and return it. If stream_to_file is True, write the output to a file."""
    logger = logging.getLogger(name)
    if cfg.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if stream_to_file:
        # Write output to a file
        formatter = FileLoggerFormatter("%(message)s")
        file_name = f"{cfg.WHOAMI}-{name}.txt"
        handler = logging.FileHandler(file_name, mode='w')  # 'w' mode overwrites the file
    else:
        # regular Stdout stream handler
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger
