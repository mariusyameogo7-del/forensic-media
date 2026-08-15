import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.app.core.database import get_db
from apps.api.app.core.errors import UnauthorizedError, NotFoundError
from apps.api.app.models.user import User, UserPreferences
from apps.api.app.models.enums import AccountType
from apps.api.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    AuthTokenResponse,
    UserPreferencesResponse,
    UserPreferencesUpdateRequest,
)

router = APIRouter(tags=["Authentification & Compte"])


def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Extracts user from Bearer token if provided."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "").strip()
    # Find or simulate authenticated user from token
    # In full Supabase integration, verify JWT signature via Supabase client
    user = db.execute(select(User).where(User.supabase_user_id == token)).scalar_one_or_none()
    return user


def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Requires authenticated user."""
    if not user:
        raise UnauthorizedError("Authentification requise pour cette action.")
    return user


@router.post("/auth/register", response_model=AuthTokenResponse)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """Registers a new standard user account."""
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise UnauthorizedError("Un compte existe déjà avec cette adresse email.")

    dummy_supabase_id = f"sub_{uuid.uuid4().hex[:16]}"
    user = User(
        supabase_user_id=dummy_supabase_id,
        email=payload.email,
        account_type=AccountType.STANDARD,
    )
    db.add(user)
    db.flush()

    preferences = UserPreferences(
        user_id=user.id,
        retain_analysis_history=True,
        retain_original_files=False,
    )
    db.add(preferences)
    db.commit()
    db.refresh(user)

    return AuthTokenResponse(
        access_token=user.supabase_user_id,
        user=UserResponse.model_validate(user)
    )


@router.post("/auth/login", response_model=AuthTokenResponse)
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Logs in an existing user."""
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if not user:
        raise UnauthorizedError("Identifiants incorrects.")

    return AuthTokenResponse(
        access_token=user.supabase_user_id,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user)):
    """Retrieves profile of the currently logged in user."""
    return UserResponse.model_validate(user)


@router.get("/me/preferences", response_model=UserPreferencesResponse)
def get_preferences(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieves privacy and retention preferences for current user."""
    prefs = db.execute(select(UserPreferences).where(UserPreferences.user_id == user.id)).scalar_one_or_none()
    if not prefs:
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return UserPreferencesResponse.model_validate(prefs)


@router.patch("/me/preferences", response_model=UserPreferencesResponse)
def update_preferences(
    payload: UserPreferencesUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates retention preferences for current user."""
    prefs = db.execute(select(UserPreferences).where(UserPreferences.user_id == user.id)).scalar_one_or_none()
    if not prefs:
        prefs = UserPreferences(user_id=user.id)
        db.add(prefs)

    if payload.retain_analysis_history is not None:
        prefs.retain_analysis_history = payload.retain_analysis_history
    if payload.retain_original_files is not None:
        prefs.retain_original_files = payload.retain_original_files

    db.commit()
    db.refresh(prefs)
    return UserPreferencesResponse.model_validate(prefs)
