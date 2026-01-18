from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import secrets
import string

from app.models.user import User, UserSession, PasswordResetToken, AuditLog
from app.schemas.auth import TokenData
from app.core.config import settings


class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = settings.SECRET_KEY
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.REFRESH_TOKEN_EXPIRE_DAYS = 30

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            token_data = TokenData(username=username)
            return token_data
        except JWTError:
            return None

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        return user

    def create_user_session(self, db: Session, user: User, user_agent: str = None, ip_address: str = None) -> Dict[str, Any]:
        """Create a new user session with tokens"""
        # Create access and refresh tokens
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role},
            expires_delta=access_token_expires
        )
        
        refresh_token = self.create_refresh_token(
            data={"sub": user.username, "user_id": user.id, "type": "refresh"}
        )
        
        # Generate session token
        session_token = self.generate_session_token()
        
        # Create session record
        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS),
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        db.add(session)
        
        # Update user last login
        user.last_login = datetime.utcnow()
        
        # Log the login
        self.log_audit_event(
            db, user.id, "login", "user", user.id, 
            f"User logged in from {ip_address}", ip_address, user_agent
        )
        
        db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "session_token": session_token,
            "token_type": "bearer",
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }

    def refresh_access_token(self, db: Session, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        token_data = self.verify_token(refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if refresh token exists in database
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or expired"
            )
        
        # Get user
        user = db.query(User).filter(User.id == session.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Update session last used
        session.last_used = datetime.utcnow()
        db.commit()
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def logout_user(self, db: Session, session_token: str) -> bool:
        """Logout user by invalidating session"""
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True
        ).first()
        
        if session:
            session.is_active = False
            
            # Log the logout
            self.log_audit_event(
                db, session.user_id, "logout", "user", session.user_id,
                "User logged out"
            )
            
            db.commit()
            return True
        
        return False

    def generate_session_token(self) -> str:
        """Generate secure session token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

    def generate_password_reset_token(self, db: Session, user: User) -> str:
        """Generate password reset token"""
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        # Invalidate existing tokens
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used == False
        ).update({"is_used": True})
        
        # Create new token
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        )
        
        db.add(reset_token)
        db.commit()
        
        return token

    def verify_password_reset_token(self, db: Session, token: str) -> Optional[User]:
        """Verify password reset token and return user"""
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.is_used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not reset_token:
            return None
        
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        return user

    def reset_password(self, db: Session, token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.is_used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not reset_token:
            return False
        
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        if not user:
            return False
        
        # Update password
        user.hashed_password = self.get_password_hash(new_password)
        
        # Mark token as used
        reset_token.is_used = True
        
        # Invalidate all user sessions
        db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).update({"is_active": False})
        
        # Log the password reset
        self.log_audit_event(
            db, user.id, "password_reset", "user", user.id,
            "Password reset successfully"
        )
        
        db.commit()
        return True

    def log_audit_event(self, db: Session, user_id: int, action: str, resource_type: str, 
                       resource_id: int = None, details: str = None, 
                       ip_address: str = None, user_agent: str = None):
        """Log audit event"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(audit_log)

    def check_permission(self, user_role: str, required_role: str) -> bool:
        """Check if user has required permission"""
        role_hierarchy = {
            "viewer": 1,
            "recruiter": 2,
            "hr_manager": 3,
            "admin": 4
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level

    def get_user_by_session(self, db: Session, session_token: str) -> Optional[User]:
        """Get user by session token"""
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        user = db.query(User).filter(
            User.id == session.user_id,
            User.is_active == True
        ).first()
        
        return user
