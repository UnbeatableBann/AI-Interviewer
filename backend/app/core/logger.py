import os
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

class AppLoggers:
    def __init__(
        self,
        log_dir: str = "logs",
        level: str = "INFO",
        max_bytes: int = 5_000_000,
        backup_count: int = 5,
        enable_console: bool = False
    ):
        self.log_dir = log_dir
        self.level = level.upper()
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.enable_console = enable_console

        os.makedirs(self.log_dir, exist_ok=True)

        self.flask = self._setup_logger("flask", "flask.log")
        self.db = self._setup_logger("db", "db.log")
        self.external_api = self._setup_logger("external_api", "external_api.log")

    def _setup_logger(self, name: str, filename: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.level, logging.INFO))
        logger.propagate = False

        if logger.handlers:
            return logger

        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s %(module)s '
            '%(lineno)d %(funcName)s %(threadName)s %(process)d',
            datefmt='%Y-%m-%dT%H:%M:%S%z'
        )

        file_path = os.path.join(self.log_dir, filename)
        file_handler = RotatingFileHandler(file_path, maxBytes=self.max_bytes, backupCount=self.backup_count, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if self.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

# Initialize all loggers in one go
loggers = AppLoggers(
    log_dir="logs",
    level="DEBUG",
    enable_console=False
)

"""
if __name__ == "__main__":
    # Example usage
    logger=AppLoggers(enable_console=True)
    logger.flask.info("flask logger is running")"""