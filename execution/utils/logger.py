"""
Logging configuration for LinkedIn Manager.

Provides structured logging with console and file outputs.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import rich for nice terminal output, fall back to standard logging
try:
    from rich.logging import RichHandler
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    import logging
    RICH_AVAILABLE = False

import logging

# Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = Path("logs")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    if RICH_AVAILABLE:
        # Use Rich handler for better formatting
        rich_handler = RichHandler(
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            markup=True
        )
        rich_handler.setLevel(logging.DEBUG)
        logger.addHandler(rich_handler)
    else:
        logger.addHandler(console_handler)
    
    # File handler (daily rotation)
    log_file = LOG_DIR / f"linkedin_manager_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Global console for nice output
if RICH_AVAILABLE:
    console = Console()
else:
    class SimpleConsole:
        def print(self, *args, **kwargs):
            print(*args, **kwargs)
        
        def rule(self, title: str):
            print(f"\n{'='*60}\n{title}\n{'='*60}\n")
    
    console = SimpleConsole()
