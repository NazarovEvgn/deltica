# backend/utils/auth.py
# Утилиты для аутентификации: хеширование паролей, создание и проверка JWT токенов

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.app.models import User

# Настройки безопасности
SECRET_KEY = "deltica_secret_key_change_in_production_2024"  # TODO: Вынести в .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа (для удобства пользователей)

# OAuth2 схема для получения токена из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ==================== ХЕШИРОВАНИЕ ПАРОЛЕЙ ====================

def hash_password(password: str) -> str:
    """Хеширование пароля с использованием bcrypt"""
    # Конвертируем пароль в bytes
    password_bytes = password.encode('utf-8')
    # Генерируем соль и хешируем
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Возвращаем как строку
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    # Конвертируем в bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # Проверяем
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ==================== JWT ТОКЕНЫ ====================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT токена

    Args:
        data: Данные для включения в токен (обычно {"sub": username})
        expires_delta: Время жизни токена (по умолчанию 24 часа)

    Returns:
        JWT токен в виде строки
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Декодирование JWT токена и получение username

    Args:
        token: JWT токен

    Returns:
        Username из токена или None если токен невалидный
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        return username
    except JWTError:
        return None


# ==================== DEPENDENCY: ПОЛУЧЕНИЕ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ ====================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency для получения текущего аутентифицированного пользователя

    Используется в защищенных endpoints: @router.get("/protected", dependencies=[Depends(get_current_user)])
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Декодируем токен
    username = decode_access_token(token)
    if username is None:
        raise credentials_exception

    # Ищем пользователя в БД
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    # Проверяем активность пользователя
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency для проверки что текущий пользователь - администратор

    Используется для endpoints доступных только админу
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


# ==================== АУТЕНТИФИКАЦИЯ ПОЛЬЗОВАТЕЛЯ ====================

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Аутентификация пользователя по логину и паролю

    Args:
        db: Сессия БД
        username: Имя пользователя
        password: Пароль (открытый текст)

    Returns:
        User объект если аутентификация успешна, иначе None
    """
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
