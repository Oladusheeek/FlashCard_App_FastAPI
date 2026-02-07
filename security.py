from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Настройки (в реальной жизни их прячут в .env)
SECRET_KEY = "my_super_secret_key_change_me" # Соль для подписи токена
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройка для хеширования (используем алгоритм bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. Функция: Превращает пароль "123" в кашу "$2b$12$..."
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 2. Функция: Проверяет, совпадает ли пароль "123" с кашей из базы
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 3. Функция: Создает JWT токен (билет на вход)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    # ИСПРАВЛЕНИЕ ЗДЕСЬ
    if expires_delta:
        # Было: expire = datetime.utcnow() + expires_delta
        expire = datetime.now(timezone.utc) + expires_delta 
    else:
        # Было: expire = datetime.utcnow() + timedelta(minutes=15)
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user_id(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception