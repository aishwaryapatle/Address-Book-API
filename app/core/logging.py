import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# When the log file reaches 5 MB, it is renamed and a new file is started.
# The 3 most recent old files are kept (app.log.1, app.log.2, app.log.3).
MAX_LOG_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3


def configure_logging() -> None:
    """Send logs to the console and to a log file that rotates."""

    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )

    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[logging.StreamHandler(), file_handler],
        force=True,
    )
