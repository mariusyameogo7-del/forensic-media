from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict
from apps.api.app.models.enums import AccountType


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    supabase_user_id: str
    email: str
    account_type: AccountType
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserPreferencesResponse(BaseModel):
    retain_analysis_history: bool
    retain_original_files: bool
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPreferencesUpdateRequest(BaseModel):
    retain_analysis_history: Optional[bool] = None
    retain_original_files: Optional[bool] = None
