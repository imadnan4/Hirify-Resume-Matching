from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class TokenData(BaseModel):
    username: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    session_token: Optional[str] = None


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: Optional[UserRole] = UserRole.VIEWER


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    session_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[int]
    details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
