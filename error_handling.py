#!/usr/bin/env python3
"""
Centralized Error Handling
Provides consistent error handling patterns with retry logic using tenacity
"""

import functools
import logging
import traceback
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass
from enum import Enum
import time

# Try to import tenacity, fall back to basic retry if not available
try:
    from tenacity import (
        retry, stop_after_attempt, wait_exponential, 
        retry_if_exception_type, before_sleep_log
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    print("⚠️ Tenacity not available, using basic retry mechanism")

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ErrorInfo:
    """Structured error information"""
    error_type: str
    message: str
    severity: ErrorSeverity
    context: Dict[str, Any]
    timestamp: float
    traceback_str: str = ""
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization"""
        return {
            'error_type': self.error_type,
            'message': self.message,
            'severity': self.severity.value,
            'context': self.context,
            'timestamp': self.timestamp,
            'traceback': self.traceback_str,
            'retry_count': self.retry_count
        }

class PDFTranslatorError(Exception):
    """Base exception for PDF translator errors"""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.context = context or {}
        self.timestamp = time.time()

class ConfigurationError(PDFTranslatorError):
    """Configuration-related errors"""
    pass

class ProcessingError(PDFTranslatorError):
    """Document processing errors"""
    pass

class TranslationError(PDFTranslatorError):
    """Translation service errors"""
    pass

class NougatError(PDFTranslatorError):
    """Nougat processing errors"""
    pass

class FileOperationError(PDFTranslatorError):
    """File operation errors"""
    pass

class ErrorCollector:
    """Collects and manages errors during processing"""
    
    def __init__(self):
        self.errors: List[ErrorInfo] = []
        self.warnings: List[ErrorInfo] = []
    
    def add_error(self, error: Union[Exception, ErrorInfo], context: Optional[Dict[str, Any]] = None):
        """Add an error to the collection"""
        if isinstance(error, ErrorInfo):
            error_info = error
        else:
            error_info = ErrorInfo(
                error_type=type(error).__name__,
                message=str(error),
                severity=ErrorSeverity.MEDIUM,
                context=context or {},
                timestamp=time.time(),
                traceback_str=traceback.format_exc()
            )
        
        if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.errors.append(error_info)
        else:
            self.warnings.append(error_info)
        
        logger.error(f"Error collected: {error_info.message}")
    
    def has_critical_errors(self) -> bool:
        """Check if there are any critical errors"""
        return any(error.severity == ErrorSeverity.CRITICAL for error in self.errors)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        return {
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'critical_errors': len([e for e in self.errors if e.severity == ErrorSeverity.CRITICAL]),
            'error_types': list(set(error.error_type for error in self.errors)),
            'warning_types': list(set(warning.error_type for warning in self.warnings))
        }

def basic_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Basic retry decorator when tenacity is not available"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            
            raise last_exception
        return wrapper
    return decorator

def with_retry(max_attempts: int = 3, 
               wait_min: float = 1.0, 
               wait_max: float = 10.0,
               retry_on: Optional[List[Type[Exception]]] = None):
    """Retry decorator with tenacity if available, basic retry otherwise"""
    
    if TENACITY_AVAILABLE:
        # Use tenacity for advanced retry logic
        retry_conditions = []
        if retry_on:
            for exc_type in retry_on:
                retry_conditions.append(retry_if_exception_type(exc_type))
        
        return retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=wait_min, max=wait_max),
            retry=retry_if_exception_type(tuple(retry_on)) if retry_on else retry_if_exception_type(Exception),
            before_sleep=before_sleep_log(logger, logging.WARNING)
        )
    else:
        # Use basic retry
        return basic_retry(max_attempts=max_attempts, delay=wait_min)

def safe_execute(func: Callable, 
                error_collector: Optional[ErrorCollector] = None,
                context: Optional[Dict[str, Any]] = None,
                default_return: Any = None) -> Any:
    """Safely execute a function with error collection"""
    try:
        return func()
    except Exception as e:
        if error_collector:
            error_collector.add_error(e, context)
        else:
            logger.error(f"Error in {func.__name__}: {e}")
        
        return default_return

def handle_api_errors(func):
    """Decorator for handling API-related errors"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_type = type(e).__name__
            
            # Classify API errors
            if "timeout" in str(e).lower():
                severity = ErrorSeverity.MEDIUM
                logger.warning(f"API timeout in {func.__name__}: {e}")
            elif "rate limit" in str(e).lower() or "quota" in str(e).lower():
                severity = ErrorSeverity.HIGH
                logger.error(f"API rate limit in {func.__name__}: {e}")
            elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                severity = ErrorSeverity.CRITICAL
                logger.critical(f"API authentication error in {func.__name__}: {e}")
            else:
                severity = ErrorSeverity.MEDIUM
                logger.error(f"API error in {func.__name__}: {e}")
            
            raise TranslationError(
                f"API error in {func.__name__}: {e}",
                severity=severity,
                context={'function': func.__name__, 'original_error': error_type}
            )
    
    return wrapper

def handle_file_operations(func):
    """Decorator for handling file operation errors"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"File operation error in {func.__name__}: {e}")
            raise FileOperationError(
                f"File operation failed in {func.__name__}: {e}",
                severity=ErrorSeverity.HIGH,
                context={'function': func.__name__, 'error_type': type(e).__name__}
            )
        except Exception as e:
            logger.error(f"Unexpected error in file operation {func.__name__}: {e}")
            raise
    
    return wrapper

def handle_processing_errors(func):
    """Decorator for handling document processing errors"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Processing error in {func.__name__}: {e}")
            raise ProcessingError(
                f"Processing failed in {func.__name__}: {e}",
                severity=ErrorSeverity.MEDIUM,
                context={'function': func.__name__, 'error_type': type(e).__name__}
            )
    
    return wrapper

class ErrorReporter:
    """Reports errors in various formats"""
    
    @staticmethod
    def generate_error_report(error_collector: ErrorCollector) -> str:
        """Generate a detailed error report"""
        report = ["📋 Error Report", "=" * 50]
        
        summary = error_collector.get_summary()
        report.append(f"Total Errors: {summary['total_errors']}")
        report.append(f"Total Warnings: {summary['total_warnings']}")
        report.append(f"Critical Errors: {summary['critical_errors']}")
        report.append("")
        
        if error_collector.errors:
            report.append("🚨 ERRORS:")
            for i, error in enumerate(error_collector.errors, 1):
                report.append(f"{i}. [{error.severity.value.upper()}] {error.error_type}: {error.message}")
                if error.context:
                    report.append(f"   Context: {error.context}")
                report.append("")
        
        if error_collector.warnings:
            report.append("⚠️ WARNINGS:")
            for i, warning in enumerate(error_collector.warnings, 1):
                report.append(f"{i}. {warning.error_type}: {warning.message}")
                if warning.context:
                    report.append(f"   Context: {warning.context}")
                report.append("")
        
        return "\n".join(report)
    
    @staticmethod
    def save_error_report(error_collector: ErrorCollector, filename: str):
        """Save error report to file"""
        try:
            report = ErrorReporter.generate_error_report(error_collector)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Error report saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save error report: {e}")

def main():
    """Test the error handling system"""
    print("🛡️ Testing Error Handling System")
    
    # Test error collector
    collector = ErrorCollector()
    
    # Test safe execution
    def failing_function():
        raise ValueError("Test error")
    
    result = safe_execute(failing_function, collector, {"test": "context"}, "default")
    print(f"Safe execution result: {result}")
    
    # Test retry decorator
    @with_retry(max_attempts=3, retry_on=[ValueError])
    def sometimes_failing_function():
        import random
        if random.random() < 0.7:
            raise ValueError("Random failure")
        return "Success!"
    
    try:
        result = sometimes_failing_function()
        print(f"Retry result: {result}")
    except Exception as e:
        print(f"Final failure: {e}")
    
    # Generate report
    report = ErrorReporter.generate_error_report(collector)
    print("\n" + report)

if __name__ == "__main__":
    main()
