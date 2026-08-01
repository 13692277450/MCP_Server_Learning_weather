import logging
import os
from datetime import datetime

from of_path_tool import get_abs_path

LOG_ROOT = get_abs_path("logs")
os.makedirs(LOG_ROOT, exist_ok=True) # type: ignore
DEFAULT_LOG_FORMAT = logging.Formatter("[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(filename)s:%(lineno)d- %(message)s")

def get_logger(
    name: str = "agent",
    level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    log_file = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    if log_file:
        return logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)
    if not log_file:
        log_file = os.path.join(LOG_ROOT,f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)
    return logger

#快捷获取日志记录器
logger = get_logger()

if __name__ == "__main__":
    logger.info("info日志")
    logger.debug("debug日志")
    logger.error("error日志")
    logger.warning("warning日志")
    logger.critical("critical日志")
