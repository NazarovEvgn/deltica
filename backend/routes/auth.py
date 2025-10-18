# backend/routes/auth.py
# API endpoints для аутентификации: login, получение информации о текущем пользователе

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from backend.core.database import get_db
from backend.app.schemas import LoginRequest, TokenResponse, UserResponse
from backend.utils.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Аутентификация пользователя и получение JWT токена

    Args:
        login_data: Логин и пароль пользователя
        db: Сессия базы данных

    Returns:
        TokenResponse с access_token и данными пользователя

    Raises:
        401: Неверный логин или пароль
        403: Пользователь деактивирован
    """
    client_ip = request.client.host if request.client else "unknown"

    # Аутентификация пользователя
    user = authenticate_user(db, login_data.username, login_data.password)

    if not user:
        logger.warning(
            f"Failed login attempt for user: {login_data.username}",
            extra={
                "event": "login_failed",
                "user": login_data.username,
                "ip": client_ip,
                "reason": "invalid_credentials"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверка активности пользователя
    if not user.is_active:
        logger.warning(
            f"Login attempt for inactive user: {user.username}",
            extra={
                "event": "login_failed",
                "user": user.username,
                "ip": client_ip,
                "reason": "user_inactive"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован. Обратитесь к администратору."
        )

    # Создание JWT токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    logger.info(
        f"Successful login: {user.username}",
        extra={
            "event": "login_success",
            "user": user.username,
            "role": user.role,
            "ip": client_ip
        }
    )

    # Формирование ответа с токеном и данными пользователя
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            department=user.department,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """
    Получение информации о текущем аутентифицированном пользователе

    Args:
        current_user: Текущий пользователь из JWT токена (dependency)

    Returns:
        UserResponse с данными пользователя

    Raises:
        401: Токен невалиден или отсутствует
        403: Пользователь неактивен
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        department=current_user.department,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


# Дополнительный endpoint для OAuth2PasswordRequestForm (для Swagger UI)
@router.post("/token", response_model=TokenResponse)
async def login_with_form(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Альтернативный endpoint для логина через форму (для Swagger UI)

    Использует стандартную OAuth2PasswordRequestForm вместо LoginRequest
    """
    client_ip = request.client.host if request.client else "unknown"
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        logger.warning(
            f"Failed login attempt (Swagger) for user: {form_data.username}",
            extra={
                "event": "login_failed",
                "user": form_data.username,
                "ip": client_ip,
                "reason": "invalid_credentials"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning(
            f"Login attempt (Swagger) for inactive user: {user.username}",
            extra={
                "event": "login_failed",
                "user": user.username,
                "ip": client_ip,
                "reason": "user_inactive"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    logger.info(
        f"Successful login (Swagger): {user.username}",
        extra={
            "event": "login_success",
            "user": user.username,
            "role": user.role,
            "ip": client_ip
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            department=user.department,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )
