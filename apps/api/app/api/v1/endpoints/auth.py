import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from apps.api.app.core.database import get_db
from apps.api.app.core.errors import UnauthorizedError, NotFoundError
from apps.api.app.core.security import hash_password, verify_password
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
    user = db.execute(select(User).where(User.supabase_user_id == token)).scalar_one_or_none()
    return user


def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Requires authenticated user."""
    if not user:
        raise UnauthorizedError("Authentification requise pour cette action.")
    return user


@router.post("/auth/register", response_model=AuthTokenResponse, summary="Créer un nouveau compte utilisateur")
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """Registers a new standard user account with email and password."""
    email_clean = payload.email.strip().lower()
    existing = db.execute(select(User).where(User.email == email_clean)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Un compte existe déjà avec cette adresse email.")

    token_secret = f"usr_{uuid.uuid4().hex}"
    user = User(
        supabase_user_id=token_secret,
        email=email_clean,
        password_hash=hash_password(payload.password),
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


@router.post("/auth/login", response_model=AuthTokenResponse, summary="Connexion d'un utilisateur existant")
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Logs in an existing user with email and password."""
    email_clean = payload.email.strip().lower()
    user = db.execute(select(User).where(User.email == email_clean)).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")

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
