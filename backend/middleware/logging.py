"""
Logging Middleware
Request/response logging with structured JSON format
"""

import logging
import json
import time
from typing import Callable, Optional
from flask import Flask, Request, Response, g, request
from functools import wraps
import uuid


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses"""
    
    def __init__(self, app: Optional[Flask] = None, logger_name: str = 'healthcare'):
        self.logger = logging.getLogger(logger_name)
        self.app = app
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
    
    def before_request(self):
        """Log request details before processing"""
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.time()
        
        # Log incoming request
        self.logger.info(
            "Incoming request",
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'content_type': request.content_type
            }
        )
    
    def after_request(self, response: Response) -> Response:
        """Log response details after processing"""
        if hasattr(g, 'request_id') and hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Log response
            self.logger.info(
                "Request completed",
                extra={
                    'request_id': g.request_id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'response_size': response.content_length or 0
                }
            )
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = g.request_id
        
        return response
    
    def teardown_request(self, exception=None):
        """Log any exceptions that occurred"""
        if exception:
            self.logger.error(
                "Request failed with exception",
                extra={
                    'request_id': g.get('request_id', 'unknown'),
                    'method': request.method,
                    'path': request.path,
                    'exception': str(exception),
                    'exception_type': type(exception).__name__
                },
                exc_info=True
            )


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'path'):
            log_data['path'] = record.path
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(
    app: Flask, 
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    json_format: bool = False
):
    """
    Setup logging configuration for the Flask app
    
    Args:
        app: Flask application instance
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        json_format: Whether to use JSON formatting
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter if json_format else logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        root_logger.addHandler(file_handler)
    
    # Set Werkzeug logging level
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    # Initialize request logging middleware
    RequestLoggingMiddleware(app)


def log_function_call(logger: Optional[logging.Logger] = None):
    """
    Decorator to log function calls
    
    Args:
        logger: Logger instance to use
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or logging.getLogger(func.__module__)
            
            log.debug(
                f"Calling {func.__name__}",
                extra={
                    'function': func.__name__,
                    'args': str(args)[:100],
                    'kwargs': str(kwargs)[:100]
                }
            )
            
            try:
                result = func(*args, **kwargs)
                log.debug(
                    f"Completed {func.__name__}",
                    extra={'function': func.__name__}
                )
                return result
            except Exception as e:
                log.error(
                    f"Error in {func.__name__}: {str(e)}",
                    extra={
                        'function': func.__name__,
                        'exception': str(e)
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator

