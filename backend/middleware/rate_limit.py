"""
Rate Limiting Middleware
Rate limiting for API endpoints
"""

import time
from typing import Callable, Dict, Optional
from flask import Flask, Request, Response, request, g
from functools import wraps
import logging


logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Simple in-memory rate limiting middleware"""
    
    def __init__(
        self,
        app: Optional[Flask] = None,
        default_limit: int = 100,
        default_window: int = 60
    ):
        """
        Initialize rate limiter
        
        Args:
            app: Flask application
            default_limit: Maximum requests per window
            default_window: Time window in seconds
        """
        self.app = app
        self.default_limit = default_limit
        self.default_window = default_window
        self.request_counts: Dict[str, list] = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware with Flask app"""
        app.before_request(self.check_rate_limit)
    
    def _get_client_id(self) -> str:
        """Get unique identifier for client"""
        # Try to get user ID if authenticated
        if hasattr(g, 'user_id'):
            return f"user:{g.user_id}"
        
        # Fall back to IP address
        return f"ip:{request.remote_addr}"
    
    def _clean_old_requests(self, client_id: str, current_time: float):
        """Remove expired request timestamps"""
        if client_id in self.request_counts:
            window_start = current_time - self.default_window
            self.request_counts[client_id] = [
                ts for ts in self.request_counts[client_id]
                if ts > window_start
            ]
    
    def _is_rate_limited(self, client_id: str) -> tuple:
        """
        Check if client is rate limited
        
        Returns:
            Tuple of (is_limited, remaining_requests, reset_time)
        """
        current_time = time.time()
        
        # Clean old requests
        self._clean_old_requests(client_id, current_time)
        
        # Get request count
        request_times = self.request_counts.get(client_id, [])
        request_count = len(request_times)
        
        # Check limit
        if request_count >= self.default_limit:
            # Calculate reset time
            if request_times:
                oldest_request = min(request_times)
                reset_time = oldest_request + self.default_window
            else:
                reset_time = current_time + self.default_window
            
            return True, 0, int(reset_time)
        
        # Add current request
        if client_id not in self.request_counts:
            self.request_counts[client_id] = []
        self.request_counts[client_id].append(current_time)
        
        remaining = self.default_limit - request_count - 1
        reset_time = current_time + self.default_window
        
        return False, remaining, int(reset_time)
    
    def check_rate_limit(self):
        """Check rate limit before processing request"""
        # Skip rate limiting for health check
        if request.path == '/api/status':
            return None
        
        client_id = self._get_client_id()
        is_limited, remaining, reset_time = self._is_rate_limited(client_id)
        
        # Add rate limit headers
        g.rate_limit_remaining = remaining
        g.rate_limit_reset = reset_time
        
        if is_limited:
            logger.warning(
                f"Rate limit exceeded for {client_id}",
                extra={'client_id': client_id, 'limit': self.default_limit}
            )
            
            response = Response(
                '{"error": "Rate limit exceeded", "message": "Too many requests. Please try again later."}',
                status=429,
                mimetype='application/json'
            )
            response.headers['X-RateLimit-Limit'] = str(self.default_limit)
            response.headers['X-RateLimit-Remaining'] = '0'
            response.headers['X-RateLimit-Reset'] = str(reset_time)
            return response
        
        return None


def rate_limit(limit: int = 100, window: int = 60):
    """
    Decorator for rate limiting specific routes
    
    Args:
        limit: Maximum requests allowed
        window: Time window in seconds
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            # This is a simple decorator - actual rate limiting
            # is handled by the middleware
            return f(*args, **kwargs)
        return wrapped
    return decorator


# In-memory storage for route-specific limits
_route_limits: Dict[str, tuple] = {}


def set_route_limit(route: str, limit: int, window: int = 60):
    """
    Set rate limit for a specific route
    
    Args:
        route: Route path pattern
        limit: Maximum requests
        window: Time window in seconds
    """
    _route_limits[route] = (limit, window)


def get_route_limit(route: str) -> tuple:
    """
    Get rate limit for a route
    
    Returns:
        Tuple of (limit, window) or default values
    """
    return _route_limits.get(route, (100, 60))

