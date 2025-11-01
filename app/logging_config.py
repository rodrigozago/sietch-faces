"""
Logging configuration for Sietch Faces API.

This module sets up structured logging for the application with appropriate
log levels, formatters, and handlers.
"""
import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure logging for the application.
    
    Sets up console logging with detailed format including timestamp,
    logger name, level, and message. Also includes exception info when available.
    
    Args:
        level (Optional[str]): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            Defaults to INFO if not specified.
            
    Example:
        >>> from app.logging_config import setup_logging
        >>> setup_logging("DEBUG")
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Application started")
    """
    log_level = getattr(logging, level.upper() if level else "INFO", logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.ERROR)
    logging.getLogger("deepface").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {logging.getLevelName(log_level)}")
