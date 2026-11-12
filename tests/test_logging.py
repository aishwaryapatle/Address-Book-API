import logging

from app.core import logging as app_logging
from app.core.config import settings


def test_logs_are_written_to_file(tmp_path, monkeypatch):
    log_file = tmp_path / "logs" / "app.log"
    monkeypatch.setattr(settings, "LOG_FILE", str(log_file))

    root = logging.getLogger()
    old_handlers = root.handlers[:]
    old_level = root.level

    try:
        app_logging.configure_logging()
        logging.getLogger("test").error("something failed")

        for handler in root.handlers:
            handler.flush()

        assert "something failed" in log_file.read_text(encoding="utf-8")
    finally:
        for handler in root.handlers[:]:
            root.removeHandler(handler)
            handler.close()
        for handler in old_handlers:
            root.addHandler(handler)
        root.setLevel(old_level)
