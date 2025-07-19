import re
import hashlib
import secrets
import mimetypes
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import ipaddress
from pathlib import Path
import magic
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.logging_config import app_logger
from app.core.database import get_db

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class SecurityConfig:
    """Security configuration and constants"""
    
    # File upload security
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_MIME_TYPES = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx']
    
    # Password security
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_PATTERNS = [
        r'(?=.*[a-z])',  # lowercase
        r'(?=.*[A-Z])',  # uppercase
        r'(?=.*\d)',     # digit
        r'(?=.*[@$!%*?&])'  # special character
    ]
    
    # Rate limiting
    RATE_LIMITS = {
        'login': '5/minute',
        'register': '3/minute',
        'upload': '10/minute',
        'api_default': '100/minute',
        'password_reset': '3/hour'
    }
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b|\bDROP\b)',
        r'(\bOR\b|\bAND\b).*=.*\b\d+\b',
        r'[\'";].*(\bOR\b|\bAND\b).*[\'";]',
        r'(\bEXEC\b|\bEXECUTE\b).*\(',
        r'(\bSP_\b|\bXP_\b)',
        r'(\bSCRIPT\b|\bJAVASCRIPT\b)',
        r'(<script|<iframe|<object|<embed)'
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
        r'<form[^>]*>',
        r'<input[^>]*>',
        r'<textarea[^>]*>',
        r'<button[^>]*>',
        r'<select[^>]*>',
        r'<option[^>]*>',
    ]


class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        issues = []
        
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            issues.append(f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters long")
        
        for pattern in SecurityConfig.PASSWORD_PATTERNS:
            if not re.search(pattern, password):
                if 'lowercase' in pattern:
                    issues.append("Password must contain at least one lowercase letter")
                elif 'uppercase' in pattern:
                    issues.append("Password must contain at least one uppercase letter")
                elif 'digit' in pattern:
                    issues.append("Password must contain at least one digit")
                elif 'special' in pattern:
                    issues.append("Password must contain at least one special character (@$!%*?&)")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'strength': SecurityValidator._calculate_password_strength(password)
        }
    
    @staticmethod
    def _calculate_password_strength(password: str) -> str:
        """Calculate password strength"""
        score = 0
        
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[@$!%*?&]', password):
            score += 1
        if len(password) >= 16:
            score += 1
        
        if score < 3:
            return "weak"
        elif score < 5:
            return "medium"
        else:
            return "strong"
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_input(input_text: str, remove_html: bool = True) -> str:
        """Sanitize user input"""
        if not input_text:
            return input_text
        
        # Remove null bytes
        sanitized = input_text.replace('\x00', '')
        
        # Remove HTML tags if requested
        if remove_html:
            sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Escape special characters
        sanitized = sanitized.replace('&', '&amp;')
        sanitized = sanitized.replace('<', '&lt;')
        sanitized = sanitized.replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;')
        sanitized = sanitized.replace("'", '&#x27;')
        
        return sanitized
    
    @staticmethod
    def detect_sql_injection(input_text: str) -> bool:
        """Detect potential SQL injection attempts"""
        if not input_text:
            return False
        
        input_lower = input_text.lower()
        
        for pattern in SecurityConfig.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def detect_xss(input_text: str) -> bool:
        """Detect potential XSS attempts"""
        if not input_text:
            return False
        
        input_lower = input_text.lower()
        
        for pattern in SecurityConfig.XSS_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def validate_file_upload(file_content: bytes, filename: str, max_size: int = None) -> Dict[str, Any]:
        """Validate uploaded file"""
        if max_size is None:
            max_size = SecurityConfig.MAX_FILE_SIZE
        
        issues = []
        
        # Check file size
        if len(file_content) > max_size:
            issues.append(f"File size exceeds maximum allowed size of {max_size} bytes")
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in SecurityConfig.ALLOWED_EXTENSIONS:
            issues.append(f"File extension '{file_ext}' is not allowed")
        
        # Check MIME type
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
            if mime_type not in SecurityConfig.ALLOWED_MIME_TYPES:
                issues.append(f"File type '{mime_type}' is not allowed")
        except Exception:
            issues.append("Could not determine file type")
        
        # Check for embedded executables or scripts
        if SecurityValidator._contains_malicious_content(file_content):
            issues.append("File contains potentially malicious content")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'mime_type': mime_type if 'mime_type' in locals() else 'unknown',
            'size': len(file_content)
        }
    
    @staticmethod
    def _contains_malicious_content(file_content: bytes) -> bool:
        """Check for malicious content in file"""
        # Check for executable signatures
        malicious_signatures = [
            b'MZ',  # Windows executable
            b'\x7fELF',  # Linux executable
            b'\xca\xfe\xba\xbe',  # Java class file
            b'PK\x03\x04',  # ZIP file (could contain executables)
        ]
        
        for signature in malicious_signatures:
            if file_content.startswith(signature):
                return True
        
        # Check for script content
        script_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'<?php',
            b'<%',
            b'#!/bin/sh',
            b'#!/bin/bash',
            b'powershell',
            b'cmd.exe',
        ]
        
        content_lower = file_content.lower()
        for pattern in script_patterns:
            if pattern in content_lower:
                return True
        
        return False


class SecurityMiddleware:
    """Security middleware for request processing"""
    
    def __init__(self):
        self.validator = SecurityValidator()
        self.blocked_ips = set()
        self.suspicious_activity = {}
    
    async def process_request(self, request: Request) -> Optional[HTTPException]:
        """Process request for security validation"""
        client_ip = get_remote_address(request)
        
        # Check blocked IPs
        if client_ip in self.blocked_ips:
            app_logger.log_security_event(
                "Blocked IP attempted access",
                ip_address=client_ip,
                details={"url": str(request.url)}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check for suspicious patterns in URL
        if self._is_suspicious_url(str(request.url)):
            await self._record_suspicious_activity(client_ip, "suspicious_url")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request"
            )
        
        # Validate headers
        if not self._validate_headers(request.headers):
            await self._record_suspicious_activity(client_ip, "invalid_headers")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request headers"
            )
        
        return None
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL contains suspicious patterns"""
        suspicious_patterns = [
            r'\.\./',  # Directory traversal
            r'%2e%2e%2f',  # Encoded directory traversal
            r'<script',  # XSS
            r'javascript:',  # XSS
            r'union.*select',  # SQL injection
            r'drop.*table',  # SQL injection
            r'exec.*\(',  # Code execution
            r'system\(',  # System command
            r'eval\(',  # Code evaluation
        ]
        
        url_lower = url.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, url_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _validate_headers(self, headers: Dict[str, str]) -> bool:
        """Validate request headers"""
        # Check for suspicious User-Agent
        user_agent = headers.get('user-agent', '').lower()
        if any(bot in user_agent for bot in ['sqlmap', 'nikto', 'nmap', 'burp']):
            return False
        
        # Check for suspicious headers
        suspicious_headers = [
            'x-forwarded-host',
            'x-real-ip',
            'x-cluster-client-ip',
            'x-original-url',
            'x-rewrite-url',
        ]
        
        for header in suspicious_headers:
            if header in headers:
                # Log but don't block (might be legitimate proxy)
                app_logger.log_security_event(
                    f"Suspicious header detected: {header}",
                    details={"value": headers[header]}
                )
        
        return True
    
    async def _record_suspicious_activity(self, ip_address: str, activity_type: str):
        """Record suspicious activity"""
        current_time = datetime.utcnow()
        
        if ip_address not in self.suspicious_activity:
            self.suspicious_activity[ip_address] = {
                'count': 0,
                'last_activity': current_time,
                'activities': []
            }
        
        self.suspicious_activity[ip_address]['count'] += 1
        self.suspicious_activity[ip_address]['last_activity'] = current_time
        self.suspicious_activity[ip_address]['activities'].append({
            'type': activity_type,
            'timestamp': current_time
        })
        
        # Auto-block after threshold
        if self.suspicious_activity[ip_address]['count'] > 10:
            self.blocked_ips.add(ip_address)
            app_logger.log_security_event(
                f"Auto-blocked IP due to suspicious activity",
                ip_address=ip_address,
                details={"activity_count": self.suspicious_activity[ip_address]['count']}
            )
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers to add to responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self):
        self.limiter = Limiter(key_func=get_remote_address)
    
    def get_limiter(self) -> Limiter:
        """Get rate limiter instance"""
        return self.limiter
    
    def create_rate_limit_decorator(self, rate: str):
        """Create rate limit decorator"""
        def decorator(func):
            return self.limiter.limit(rate)(func)
        return decorator


class InputValidator(BaseModel):
    """Base input validator with security checks"""
    
    @validator('*', pre=True)
    def validate_input_security(cls, v):
        """Validate input for security issues"""
        if isinstance(v, str):
            # Check for SQL injection
            if SecurityValidator.detect_sql_injection(v):
                raise ValueError("Input contains potentially malicious content")
            
            # Check for XSS
            if SecurityValidator.detect_xss(v):
                raise ValueError("Input contains potentially malicious content")
            
            # Sanitize input
            v = SecurityValidator.sanitize_input(v)
        
        return v


class SecureFileUpload:
    """Secure file upload handler"""
    
    def __init__(self, max_size: int = None, allowed_extensions: List[str] = None):
        self.max_size = max_size or SecurityConfig.MAX_FILE_SIZE
        self.allowed_extensions = allowed_extensions or SecurityConfig.ALLOWED_EXTENSIONS
        self.validator = SecurityValidator()
    
    async def validate_and_save(self, file_content: bytes, filename: str, 
                               upload_dir: str = "uploads") -> Dict[str, Any]:
        """Validate and save uploaded file"""
        # Validate file
        validation_result = self.validator.validate_file_upload(
            file_content, filename, self.max_size
        )
        
        if not validation_result['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File validation failed: {', '.join(validation_result['issues'])}"
            )
        
        # Generate secure filename
        secure_filename = self._generate_secure_filename(filename)
        
        # Create upload directory if it doesn't exist
        upload_path = Path(upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_path / secure_filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Log file upload
        app_logger.log_security_event(
            "File uploaded",
            details={
                "filename": secure_filename,
                "size": len(file_content),
                "mime_type": validation_result['mime_type']
            }
        )
        
        return {
            'filename': secure_filename,
            'path': str(file_path),
            'size': len(file_content),
            'mime_type': validation_result['mime_type']
        }
    
    def _generate_secure_filename(self, filename: str) -> str:
        """Generate secure filename"""
        # Get file extension
        file_ext = Path(filename).suffix.lower()
        
        # Generate secure base name
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        random_suffix = secrets.token_hex(8)
        secure_name = f"{timestamp}_{random_suffix}{file_ext}"
        
        return secure_name


# Global instances
security_middleware = SecurityMiddleware()
rate_limiter = RateLimiter()
security_validator = SecurityValidator()
secure_file_upload = SecureFileUpload()


# Security dependencies
def get_security_headers():
    """Dependency to add security headers"""
    return security_middleware.get_security_headers()


def validate_request_security():
    """Dependency to validate request security"""
    async def _validate(request: Request):
        result = await security_middleware.process_request(request)
        if result:
            raise result
    return _validate


def get_rate_limiter():
    """Dependency to get rate limiter"""
    return rate_limiter.get_limiter()


# JWT Authentication Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return username"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(token)
    if username is None:
        raise credentials_exception
    
    # Import here to avoid circular import
    from app.services.auth_service import AuthService
    auth_service = AuthService()
    
    user = await auth_service.get_user_by_email(db, username)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def create_password_reset_token(email: str) -> str:
    """Create password reset token"""
    delta = timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "sub": email, "type": "password_reset"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type = payload.get("type")
        if token_type != "password_reset":
            return None
        email = payload.get("sub")
        return email
    except JWTError:
        return None


def create_email_verification_token(email: str) -> str:
    """Create email verification token"""
    delta = timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "sub": email, "type": "email_verification"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[str]:
    """Verify email verification token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type = payload.get("type")
        if token_type != "email_verification":
            return None
        email = payload.get("sub")
        return email
    except JWTError:
        return None
