import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

from job.models import User

SECRET_KEY = os.environ.get("SECRET_KEY")
token_expiration_minutes = int(os.environ.get('TOKEN_EXPIRATION_MINUTES')) \
    if os.environ.get('TOKEN_EXPIRATION_MINUTES') is not None \
    else 15
token_refresh_last_minutes = int(os.environ.get('TOKEN_REFRESH_LAST_MINUTES')) \
    if os.environ.get('TOKEN_REFRESH_LAST_MINUTES') is not None \
    else 10

algorithm = os.environ.get('ALGORITHM')

ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=token_expiration_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=algorithm)
    return encoded_jwt


def get_token_remaining_time(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        exp_timestamp = payload["exp"]
        remaining_time = exp_timestamp - datetime.utcnow().timestamp()
        return remaining_time if remaining_time > 0 else 0
    except jwt.exceptions.DecodeError:
        return 0