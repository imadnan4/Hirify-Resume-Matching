import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling for the application"""
    
    def __init__(self):
        self.error_codes = {
            # Client errors (4xx)
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            422: "Validation Error",
            429: "Too Many Requests",
            
            # Server errors (5xx)
            500: "Internal Server Error",
            501: "Not Implemented",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout"
        }
    
    def create_error_response(
        self, 
        error_code: int, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        response = {
            "error": {
                "code": error_code,
                "message": message,
                "type": self.error_codes.get(error_code, "Unknown Error"),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        if request_id:
            response["error"]["request_id"] = request_id
            
        return response
    
    def log_error(
        self, 
        error: Exception, 
        request: Optional[Request] = None,
        user_id: Optional[int] = None,
        extra_context: Optional[Dict[str, Any]] = None
    ):
        """Log error with context information"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "traceback": traceback.format_exc()
        }
        
        if request:
            error_info.update({
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client_ip": request.client.host if request.client else None
            })
        
        if user_id:
            error_info["user_id"] = user_id
            
        if extra_context:
            error_info["context"] = extra_context
        
        logger.error(f"Application Error: {error_info}")
        
        # You could also send to external error tracking service here
        # self.send_to_error_tracking(error_info)
    
    def handle_validation_error(self, error: ValidationError) -> Dict[str, Any]:
        """Handle Pydantic validation errors"""
        details = []
        for err in error.errors():
            details.append({
                "field": ".".join(str(x) for x in err["loc"]),
                "message": err["msg"],
                "type": err["type"]
            })
        
        return self.create_error_response(
            422,
            "Validation failed",
            {"validation_errors": details}
        )
    
    def handle_database_error(self, error: SQLAlchemyError) -> Dict[str, Any]:
        """Handle database errors"""
        if isinstance(error, IntegrityError):
            return self.create_error_response(
                409,
                "Data integrity constraint violation",
                {"database_error": "The operation violates database constraints"}
            )
        
        return self.create_error_response(
            500,
            "Database operation failed",
            {"database_error": "An error occurred while accessing the database"}
        )
    
    def handle_file_processing_error(self, error: Exception) -> Dict[str, Any]:
        """Handle file processing errors"""
        error_message = str(error)
        
        if "file format" in error_message.lower():
            return self.create_error_response(
                400,
                "Unsupported file format",
                {"file_error": "The uploaded file format is not supported"}
            )
        
        if "file size" in error_message.lower():
            return self.create_error_response(
                413,
                "File too large",
                {"file_error": "The uploaded file exceeds the maximum size limit"}
            )
        
        if "corrupted" in error_message.lower():
            return self.create_error_response(
                400,
                "File corrupted",
                {"file_error": "The uploaded file appears to be corrupted"}
            )
        
        return self.create_error_response(
            500,
            "File processing failed",
            {"file_error": "An error occurred while processing the file"}
        )
    
    def handle_nlp_error(self, error: Exception) -> Dict[str, Any]:
        """Handle NLP processing errors"""
        error_message = str(error)
        
        if "model" in error_message.lower():
            return self.create_error_response(
                503,
                "NLP service unavailable",
                {"nlp_error": "The NLP service is temporarily unavailable"}
            )
        
        if "timeout" in error_message.lower():
            return self.create_error_response(
                504,
                "Processing timeout",
                {"nlp_error": "The NLP processing took too long to complete"}
            )
        
        return self.create_error_response(
            500,
            "NLP processing failed",
            {"nlp_error": "An error occurred during natural language processing"}
        )
    
    def handle_authentication_error(self, error: Exception) -> Dict[str, Any]:
        """Handle authentication errors"""
        error_message = str(error)
        
        if "expired" in error_message.lower():
            return self.create_error_response(
                401,
                "Token expired",
                {"auth_error": "The authentication token has expired"}
            )
        
        if "invalid" in error_message.lower():
            return self.create_error_response(
                401,
                "Invalid credentials",
                {"auth_error": "The provided credentials are invalid"}
            )
        
        return self.create_error_response(
            401,
            "Authentication failed",
            {"auth_error": "Authentication is required to access this resource"}
        )
    
    def handle_authorization_error(self, error: Exception) -> Dict[str, Any]:
        """Handle authorization errors"""
        return self.create_error_response(
            403,
            "Insufficient permissions",
            {"auth_error": "You don't have permission to access this resource"}
        )
    
    def handle_rate_limit_error(self, error: Exception) -> Dict[str, Any]:
        """Handle rate limiting errors"""
        return self.create_error_response(
            429,
            "Rate limit exceeded",
            {"rate_limit": "Too many requests. Please try again later."}
        )
    
    def get_user_friendly_message(self, error: Exception) -> str:
        """Get user-friendly error message"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Map technical errors to user-friendly messages
        friendly_messages = {
            "ValidationError": "Please check your input data and try again.",
            "SQLAlchemyError": "There was a problem with the database. Please try again.",
            "FileNotFoundError": "The requested file could not be found.",
            "PermissionError": "You don't have permission to perform this action.",
            "TimeoutError": "The operation took too long to complete. Please try again.",
            "ConnectionError": "Unable to connect to the service. Please check your connection.",
            "ValueError": "Invalid input data. Please check your data and try again.",
            "TypeError": "Invalid data type. Please check your input format.",
        }
        
        return friendly_messages.get(error_type, "An unexpected error occurred. Please try again.")
    
    def should_expose_error_details(self, error: Exception) -> bool:
        """Determine if error details should be exposed to the client"""
        # Don't expose sensitive error details in production
        sensitive_errors = [
            "DatabaseError",
            "SQLAlchemyError",
            "ConfigurationError",
            "SecurityError"
        ]
        
        return type(error).__name__ not in sensitive_errors


# Global error handler instance
error_handler = ErrorHandler()


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    error_handler.log_error(exc, request)
    
    response_data = error_handler.create_error_response(
        exc.status_code,
        exc.detail,
        request_id=getattr(request.state, 'request_id', None)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions"""
    error_handler.log_error(exc, request)
    
    response_data = error_handler.handle_validation_error(exc)
    
    return JSONResponse(
        status_code=422,
        content=response_data
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    error_handler.log_error(exc, request)
    
    # Determine appropriate error response based on exception type
    if isinstance(exc, SQLAlchemyError):
        response_data = error_handler.handle_database_error(exc)
        status_code = 500
    elif isinstance(exc, ValidationError):
        response_data = error_handler.handle_validation_error(exc)
        status_code = 422
    elif "file" in str(exc).lower():
        response_data = error_handler.handle_file_processing_error(exc)
        status_code = 400
    elif "nlp" in str(exc).lower() or "model" in str(exc).lower():
        response_data = error_handler.handle_nlp_error(exc)
        status_code = 500
    elif "auth" in str(exc).lower():
        response_data = error_handler.handle_authentication_error(exc)
        status_code = 401
    elif "permission" in str(exc).lower():
        response_data = error_handler.handle_authorization_error(exc)
        status_code = 403
    elif "rate" in str(exc).lower():
        response_data = error_handler.handle_rate_limit_error(exc)
        status_code = 429
    else:
        # Generic error response
        user_friendly_message = error_handler.get_user_friendly_message(exc)
        response_data = error_handler.create_error_response(
            500,
            user_friendly_message,
            {"error_type": type(exc).__name__} if error_handler.should_expose_error_details(exc) else None,
            request_id=getattr(request.state, 'request_id', None)
        )
        status_code = 500
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )
