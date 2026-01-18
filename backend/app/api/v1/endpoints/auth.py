from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_current_user,
    get_current_active_user,
    verify_password,
    get_password_hash,
)
from app.schemas.auth import (
    Token,
    RegisterRequest,
    UserResponse,
    LoginRequest,
    ChangePasswordRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserUpdateRequest
)
from app.services.auth_service import AuthService
from app.core.logging_config import app_logger

router = APIRouter()
# AuthService will be created on-demand to avoid startup delays


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    try:
        # Initialize auth service on-demand
        auth_service = AuthService()
        
        # Check if user already exists
        if await auth_service.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = await auth_service.create_user(db, user_data)
        
        app_logger.log_user_action(
            f"User registered: {user.email}",
            user_id=user.id,
            action="register"
        )
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.log_system_event(f"Registration error: {str(e)}", level="ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    User login with email and password
    """
    try:
        # Initialize auth service on-demand
        auth_service = AuthService()
        
        # Authenticate user
        user = await auth_service.authenticate_user(
            db, form_data.username, form_data.password
        )
        
        if not user:
            app_logger.log_security_event(
                "Failed login attempt",
                details={"email": form_data.username}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Update last login
        await auth_service.update_last_login(db, user.id)
        
        app_logger.log_user_action(
            f"User logged in: {user.email}",
            user_id=user.id,
            action="login"
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": UserResponse.from_orm(user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.log_system_event(f"Login error: {str(e)}", level="ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: Any = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Refresh access token
    """
    try:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.email}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": UserResponse.from_orm(current_user)
        }
        
    except Exception as e:
        app_logger.log_system_event(f"Token refresh error: {str(e)}", level="ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Any = Depends(get_current_active_user)
):
    """
    Get current user information
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdateRequest,
    current_user: Any = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    """
    try:
        # Initialize auth service on-demand
        auth_service = AuthService()
        updated_user = await auth_service.update_user(
            db, current_user.id, user_update
        )
        
        app_logger.log_user_action(
            f"User profile updated: {current_user.email}",
            user_id=current_user.id,
            action="profile_update"
        )
        
        return UserResponse.from_orm(updated_user)
        
    except Exception as e:
        app_logger.log_system_event(f"Profile update error: {str(e)}", level="ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Any = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        # Initialize auth service on-demand
        auth_service = AuthService()
        success = await auth_service.change_password(
            db, current_user.id, password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed"
            )
        
        app_logger.log_user_action(
            f"Password changed: {current_user.email}",
            user_id=current_user.id,
            action="password_change"
        )
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.log_error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/forgot-password")
async def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Request password reset
    """
    try:
        # Initialize auth service on-demand
        auth_service = AuthService()
        
        # Check if user exists
        user = await auth_service.get_user_by_email(db, email)
        if not user:
            # Don't reveal if email exists or not
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Generate reset token
        reset_token = await auth_service.create_password_reset_token(db, user.id)
        
        # TODO: Send email with reset link
        # await send_password_reset_email(user.email, reset_token)
        
        app_logger.log_user_action(
            f"Password reset requested: {email}",
            user_id=user.id,
            action="password_reset_request"
        )
        
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        app_logger.log_error(f"Password reset request error: {str(e)}")
        return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using reset token
    """
    try:
        # Initialize auth service on-demand
        auth_service = AuthService()
        
        # Verify and use reset token
        user = await auth_service.verify_password_reset_token(
            db, reset_data.token
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update password
        success = await auth_service.change_password(
            db, user.id, reset_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password reset failed"
            )
        
        app_logger.log_user_action(
            f"Password reset completed: {user.email}",
            user_id=user.id,
            action="password_reset_complete"
        )
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.log_error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/logout")
async def logout(
    current_user: Any = Depends(get_current_active_user),
):
    """
    Logout user (client should delete token)
    """
    app_logger.log_user_action(
        f"User logged out: {current_user.email}",
        user_id=current_user.id,
        action="logout"
    )
    
    return {"message": "Successfully logged out"}


@router.delete("/delete-account")
async def delete_account(
    current_user: Any = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account
    """
    try:
        # Initialize auth service on-demand
        auth_service = AuthService()
        success = await auth_service.delete_user(db, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Account deletion failed"
            )
        
        app_logger.log_user_action(
            f"Account deleted: {current_user.email}",
            user_id=current_user.id,
            action="account_deletion"
        )
        
        return {"message": "Account deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.log_error(f"Account deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )


@router.get("/verify-email/{token}")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify email address
    """
    try:
        # Initialize auth service on-demand
        auth_service = AuthService()
        user = await auth_service.verify_email_token(db, token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        app_logger.log_user_action(
            f"Email verified: {user.email}",
            user_id=user.id,
            action="email_verification"
        )
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.log_error(f"Email verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )
