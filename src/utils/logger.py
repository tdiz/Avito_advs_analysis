"""
Модуль настройки логирования
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str = "avito_bot",
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Настройка логгера

    Args:
        name: Имя логгера
        log_level: Уровень логирования
        log_to_file: Логировать в файл
        log_dir: Директория для логов

    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Вывод в файл
    if log_to_file:
        Path(log_dir).mkdir(exist_ok=True)
        log_file = Path(log_dir) / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
