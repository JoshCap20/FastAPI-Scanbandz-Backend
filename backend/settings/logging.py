import logging
import asyncio

class AsyncLogger:

    _log_file = "warnings.log"
    _file_handler = None
    _console_handler = None
    _logger = None  # Global logger instance

    _console_log_level = logging.INFO
    _file_log_level = logging.INFO
    
    _date_format = "%d/%m/%Y %H:%M:%S"
    _log_format = "[%(asctime)s] %(levelname)s - %(message)s"

    @classmethod
    def _get_logger(cls):
        if cls._logger is None:
            cls._logger = logging.getLogger(__name__)
            cls._logger.setLevel(cls._console_log_level)
            cls._logger.addHandler(cls._get_file_handler())
            cls._logger.addHandler(cls._get_console_handler())
        return cls._logger

    @classmethod
    def _get_file_handler(cls):
        if cls._file_handler is None:
            cls._file_handler = logging.FileHandler(cls._log_file)
            cls._file_handler.setLevel(cls._file_log_level)
            formatter = logging.Formatter(cls._log_format, datefmt=cls._date_format)
            cls._file_handler.setFormatter(formatter)
        return cls._file_handler

    @classmethod
    def _get_console_handler(cls):
        if cls._console_handler is None:
            cls._console_handler = logging.StreamHandler()
            cls._console_handler.setLevel(cls._console_log_level)
            formatter = logging.Formatter(cls._log_format, datefmt=cls._date_format)
            cls._console_handler.setFormatter(formatter)
        return cls._console_handler
    
    @classmethod
    async def log(cls, level: int, service: str, msg: str) -> None:
        await asyncio.to_thread(cls._get_logger().log, level, f"[{service}] {msg}")

    @classmethod
    async def log_error(cls, service: str, msg: str) -> None:
        await cls.log(logging.ERROR, service, msg)

    @classmethod
    async def log_warning(cls, service: str, msg: str) -> None:
        await cls.log(logging.WARNING, service, msg)

    @classmethod
    async def log_info(cls, service: str, msg: str) -> None:
        await cls.log(logging.INFO, service, msg)
