"""
Конфигурация логгера
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("database")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

file_handler = RotatingFileHandler(
    log_dir / "database.log",
    maxBytes=10 * 1024 * 1024, 
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
