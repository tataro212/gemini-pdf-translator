#!/usr/bin/env python3
"""
Structured Logging Configuration
Provides centralized logging setup for the PDF translator project
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class PDFTranslatorLogger:
    """Centralized logger configuration for PDF translator"""
    
    def __init__(self, 
                 log_level: str = "INFO",
                 log_to_file: bool = True,
                 log_to_console: bool = True,
                 log_directory: str = "logs",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        
        self.log_level = getattr(logging, log_level.upper())
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console
        self.log_directory = Path(log_directory)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Create log directory if it doesn't exist
        if self.log_to_file:
            self.log_directory.mkdir(exist_ok=True)
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if self.log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            
            # Use colored formatter for console
            console_formatter = ColoredFormatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if self.log_to_file:
            # Main log file
            main_log_file = self.log_directory / "pdf_translator.log"
            file_handler = logging.handlers.RotatingFileHandler(
                main_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            
            # Detailed formatter for file
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | %(lineno)-4d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
            
            # Error-only log file
            error_log_file = self.log_directory / "pdf_translator_errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name"""
        return logging.getLogger(name)
    
    def log_system_info(self):
        """Log system information for debugging"""
        logger = self.get_logger("system_info")
        
        logger.info("=== PDF Translator System Information ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {sys.platform}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Log level: {logging.getLevelName(self.log_level)}")
        logger.info(f"Log directory: {self.log_directory.absolute()}")
        logger.info("==========================================")
    
    def create_session_logger(self, session_id: Optional[str] = None) -> logging.Logger:
        """Create a session-specific logger"""
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        session_logger = self.get_logger(f"session_{session_id}")
        
        if self.log_to_file:
            # Create session-specific log file
            session_log_file = self.log_directory / f"session_{session_id}.log"
            session_handler = logging.FileHandler(session_log_file, encoding='utf-8')
            session_handler.setLevel(self.log_level)
            
            session_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            session_handler.setFormatter(session_formatter)
            session_logger.addHandler(session_handler)
        
        return session_logger

# Global logger instance
_logger_instance: Optional[PDFTranslatorLogger] = None

def setup_logging(log_level: str = "INFO", 
                 log_to_file: bool = True,
                 log_to_console: bool = True,
                 log_directory: str = "logs") -> PDFTranslatorLogger:
    """Setup global logging configuration"""
    global _logger_instance
    
    _logger_instance = PDFTranslatorLogger(
        log_level=log_level,
        log_to_file=log_to_file,
        log_to_console=log_to_console,
        log_directory=log_directory
    )
    
    # Log system info
    _logger_instance.log_system_info()
    
    return _logger_instance

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    if _logger_instance is None:
        setup_logging()
    
    return _logger_instance.get_logger(name)

def create_session_logger(session_id: Optional[str] = None) -> logging.Logger:
    """Create a session-specific logger"""
    if _logger_instance is None:
        setup_logging()
    
    return _logger_instance.create_session_logger(session_id)

class LoggingContext:
    """Context manager for temporary logging level changes"""
    
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.new_level = level
        self.old_level = logger.level
    
    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)

def with_debug_logging(logger: logging.Logger):
    """Context manager to temporarily enable debug logging"""
    return LoggingContext(logger, logging.DEBUG)

def with_quiet_logging(logger: logging.Logger):
    """Context manager to temporarily reduce logging to warnings and errors"""
    return LoggingContext(logger, logging.WARNING)

def main():
    """Test the logging configuration"""
    # Setup logging
    logger_config = setup_logging(log_level="DEBUG")
    
    # Test different loggers
    main_logger = get_logger("main")
    test_logger = get_logger("test_module")
    session_logger = create_session_logger("test_session")
    
    # Test different log levels
    main_logger.debug("This is a debug message")
    main_logger.info("This is an info message")
    main_logger.warning("This is a warning message")
    main_logger.error("This is an error message")
    
    test_logger.info("Message from test module")
    session_logger.info("Message from session logger")
    
    # Test context managers
    with with_debug_logging(main_logger):
        main_logger.debug("Debug message with temporary debug level")
    
    with with_quiet_logging(main_logger):
        main_logger.info("This info message should not appear")
        main_logger.warning("This warning should appear")
    
    print("✅ Logging configuration test completed")

if __name__ == "__main__":
    main()
