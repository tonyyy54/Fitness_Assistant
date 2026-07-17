from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.dependencies import DatabaseSession
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import (
    EmailAlreadyRegisteredError,
    authenticate_user,
    create_user,
)
from app.utils.security import create_access_token

LoginForm = Annotated[OAuth2PasswordRequestForm, Depends()]

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    database_session: DatabaseSession,
) -> UserResponse:
    """注册一个新用户。"""

    try:
        user = create_user(
            database_session,
            user_data,
        )
        database_session.commit()
        database_session.refresh(user)
    except EmailAlreadyRegisteredError as error:
        database_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from error

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    form_data: LoginForm,
    database_session: DatabaseSession,
) -> TokenResponse:
    """使用邮箱和密码登录。"""

    user = authenticate_user(
        database_session,
        email=form_data.username,
        password=form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=str(user.id),
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )
