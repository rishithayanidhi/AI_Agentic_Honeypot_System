"""
API Middleware for Rate Limiting, Request Validation, and Performance
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple token bucket rate limiter to prevent abuse.
    
    Limits requests per IP address to prevent DOS attacks and abuse.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.clients: Dict[str, Tuple[int, float]] = {}  # {ip: (count, window_start)}
        self.window_size = 60  # 1 minute window
    
    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiter."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean up old entries (simple cleanup every 100 requests)
        if len(self.clients) > 100:
            current_time = time.time()
            self.clients = {
                ip: (count, window_start)
                for ip, (count, window_start) in self.clients.items()
                if current_time - window_start < self.window_size * 2
            }
        
        # Check rate limit
        current_time = time.time()
        
        if client_ip in self.clients:
            count, window_start = self.clients[client_ip]
            
            # Reset window if expired
            if current_time - window_start > self.window_size:
                self.clients[client_ip] = (1, current_time)
            else:
                # Increment counter
                if count >= self.requests_per_minute:
                    logger.warning(f"⚠️ Rate limit exceeded for {client_ip}: {count} requests")
                    return JSONResponse(
                        status_code=429,
                        content={
                            "status": "error",
                            "detail": "Rate limit exceeded. Please try again later.",
                            "retry_after": int(self.window_size - (current_time - window_start))
                        }
                    )
                self.clients[client_ip] = (count + 1, window_start)
        else:
            self.clients[client_ip] = (1, current_time)
        
        # Process request
        response = await call_next(request)
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize incoming requests for security."""
    
    def __init__(self, app, max_body_size: int = 1048576):  # 1MB default
        super().__init__(app)
        self.max_body_size = max_body_size
    
    async def dispatch(self, request: Request, call_next):
        """Validate request before processing."""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            logger.warning(f"⚠️ Request body too large: {content_length} bytes")
            return JSONResponse(
                status_code=413,
                content={
                    "status": "error",
                    "detail": f"Request body too large. Maximum size: {self.max_body_size} bytes"
                }
            )
        
        # Process request
        response = await call_next(request)
        return response


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Monitor request performance and log slow requests."""
    
    def __init__(self, app, slow_request_threshold: float = 5.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
    
    async def dispatch(self, request: Request, call_next):
        """Monitor request performance."""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log slow requests
        if duration > self.slow_request_threshold:
            logger.warning(
                f"🐌 Slow request: {request.method} {request.url.path} "
                f"took {duration:.2f}s (threshold: {self.slow_request_threshold}s)"
            )
        else:
            logger.debug(f"✅ {request.method} {request.url.path} - {duration*1000:.0f}ms")
        
        # Add performance header
        response.headers["X-Response-Time"] = f"{duration*1000:.2f}ms"
        
        return response
