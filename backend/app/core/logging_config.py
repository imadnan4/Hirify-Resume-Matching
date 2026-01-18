import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from app.core.config import settings


class CustomFormatter(logging.Formatter):
    """Custom formatter with colors and structured format"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to level name
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            record.levelname = f"{color}{record.levelname}{reset}"
        
        # Add structured information
        if hasattr(record, 'user_id'):
            record.user_info = f"[User: {record.user_id}]"
        else:
            record.user_info = ""
        
        if hasattr(record, 'request_id'):
            record.request_info = f"[Request: {record.request_id}]"
        else:
            record.request_info = ""
        
        return super().format(record)


class StructuredLogger:
    """Structured logging for the application"""
    
    def __init__(self, name: str = "hirify"):
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Set logging level
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        console_formatter = CustomFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(user_info)s%(request_info)s - %(message)s'
        )
        
        # File handler for general logs
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # File handler for errors
        error_file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "errors.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Performance log handler
        perf_handler = logging.handlers.RotatingFileHandler(
            log_dir / "performance.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(file_formatter)
        
        # Create performance logger
        self.perf_logger = logging.getLogger("performance")
        self.perf_logger.addHandler(perf_handler)
        self.perf_logger.setLevel(logging.INFO)
    
    def log_request(self, method: str, url: str, user_id: Optional[int] = None, 
                   request_id: Optional[str] = None, duration: Optional[float] = None):
        """Log HTTP requests"""
        extra = {}
        if user_id:
            extra['user_id'] = user_id
        if request_id:
            extra['request_id'] = request_id
        
        message = f"HTTP {method} {url}"
        if duration:
            message += f" - Duration: {duration:.3f}s"
        
        self.logger.info(message, extra=extra)
    
    def log_user_action(self, action: str, user_id: int, details: Optional[Dict[str, Any]] = None,
                       request_id: Optional[str] = None):
        """Log user actions"""
        extra = {'user_id': user_id}
        if request_id:
            extra['request_id'] = request_id
        
        message = f"User Action: {action}"
        if details:
            message += f" - Details: {details}"
        
        self.logger.info(message, extra=extra)
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
        """Log performance metrics"""
        message = f"Performance: {operation} took {duration:.3f}s"
        if details:
            message += f" - Details: {details}"
        
        self.perf_logger.info(message)
    
    def log_business_event(self, event: str, details: Optional[Dict[str, Any]] = None,
                          user_id: Optional[int] = None):
        """Log business events"""
        extra = {}
        if user_id:
            extra['user_id'] = user_id
        
        message = f"Business Event: {event}"
        if details:
            message += f" - Details: {details}"
        
        self.logger.info(message, extra=extra)
    
    def log_security_event(self, event: str, user_id: Optional[int] = None, 
                          ip_address: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log security events"""
        extra = {}
        if user_id:
            extra['user_id'] = user_id
        
        message = f"Security Event: {event}"
        if ip_address:
            message += f" - IP: {ip_address}"
        if details:
            message += f" - Details: {details}"
        
        self.logger.warning(message, extra=extra)
    
    def log_system_event(self, event: str, level: str = "INFO", details: Optional[Dict[str, Any]] = None):
        """Log system events"""
        message = f"System Event: {event}"
        if details:
            message += f" - Details: {details}"
        
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, message)
    
    def log_task_start(self, task_name: str, task_id: str, details: Optional[Dict[str, Any]] = None):
        """Log task start"""
        message = f"Task Started: {task_name} [{task_id}]"
        if details:
            message += f" - Details: {details}"
        
        self.logger.info(message)
    
    def log_task_complete(self, task_name: str, task_id: str, duration: float, 
                         success: bool = True, details: Optional[Dict[str, Any]] = None):
        """Log task completion"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Task {status}: {task_name} [{task_id}] - Duration: {duration:.3f}s"
        if details:
            message += f" - Details: {details}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_nlp_processing(self, operation: str, text_length: int, duration: float, 
                          results_count: Optional[int] = None):
        """Log NLP processing operations"""
        message = f"NLP Processing: {operation} - Text Length: {text_length} chars - Duration: {duration:.3f}s"
        if results_count is not None:
            message += f" - Results: {results_count}"
        
        self.perf_logger.info(message)
    
    def log_database_query(self, query_type: str, table: str, duration: float, 
                          rows_affected: Optional[int] = None):
        """Log database queries"""
        message = f"Database Query: {query_type} on {table} - Duration: {duration:.3f}s"
        if rows_affected is not None:
            message += f" - Rows: {rows_affected}"
        
        self.perf_logger.info(message)
    
    def log_file_processing(self, operation: str, filename: str, file_size: int, 
                           duration: float, success: bool = True):
        """Log file processing operations"""
        status = "SUCCESS" if success else "FAILED"
        message = f"File Processing {status}: {operation} - File: {filename} - Size: {file_size} bytes - Duration: {duration:.3f}s"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_cache_operation(self, operation: str, key: str, hit: bool = None, duration: Optional[float] = None):
        """Log cache operations"""
        message = f"Cache {operation}: {key}"
        if hit is not None:
            message += f" - {'HIT' if hit else 'MISS'}"
        if duration:
            message += f" - Duration: {duration:.3f}s"
        
        self.logger.debug(message)
    
    def log_api_rate_limit(self, endpoint: str, user_id: Optional[int] = None, 
                          ip_address: Optional[str] = None, current_count: int = 0):
        """Log API rate limiting events"""
        extra = {}
        if user_id:
            extra['user_id'] = user_id
        
        message = f"Rate Limit: {endpoint} - Count: {current_count}"
        if ip_address:
            message += f" - IP: {ip_address}"
        
        self.logger.warning(message, extra=extra)
    
    def log_export_operation(self, export_type: str, format: str, record_count: int, 
                           duration: float, file_size: Optional[int] = None):
        """Log export operations"""
        message = f"Export: {export_type} to {format} - Records: {record_count} - Duration: {duration:.3f}s"
        if file_size:
            message += f" - Size: {file_size} bytes"
        
        self.logger.info(message)
    
    def log_health_check(self, service: str, status: str, response_time: float, 
                        details: Optional[Dict[str, Any]] = None):
        """Log health check results"""
        message = f"Health Check: {service} - Status: {status} - Response Time: {response_time:.3f}s"
        if details:
            message += f" - Details: {details}"
        
        if status == "healthy":
            self.logger.debug(message)
        else:
            self.logger.warning(message)


# Global logger instance
app_logger = StructuredLogger()


def get_logger(name: str = "hirify") -> StructuredLogger:
    """Get logger instance"""
    return StructuredLogger(name)


# Context manager for logging operations
class LogOperation:
    """Context manager for logging operations with timing"""
    
    def __init__(self, operation_name: str, logger: Optional[StructuredLogger] = None, 
                 log_level: str = "INFO", extra_details: Optional[Dict[str, Any]] = None):
        self.operation_name = operation_name
        self.logger = logger or app_logger
        self.log_level = log_level
        self.extra_details = extra_details or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log_system_event(
            f"Started: {self.operation_name}",
            level=self.log_level,
            details=self.extra_details
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            
            if exc_type is None:
                self.logger.log_system_event(
                    f"Completed: {self.operation_name} - Duration: {duration:.3f}s",
                    level=self.log_level,
                    details=self.extra_details
                )
            else:
                self.logger.log_system_event(
                    f"Failed: {self.operation_name} - Duration: {duration:.3f}s - Error: {exc_val}",
                    level="ERROR",
                    details=self.extra_details
                )
