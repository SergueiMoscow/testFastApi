import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from passlib.context import CryptContext

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
# ```
#
# В этом примере мы используем библиотеку `passlib` для хэширования паролей и библиотеку `PyJWT` для работы с
# токенами JWT. Мы также определяем некоторые константы, такие как секретный ключ и время жизни токена.
#
# Функция `create_access_token()` используется для создания токена JWT на основе переданных данных. Функция
# `verify_token()` используется для проверки токена и возвращает данные, содержащиеся в токене, если токен
# действительный. Функции `get_password_hash()` и `verify_password()` используются для хэширования и проверки паролей.
