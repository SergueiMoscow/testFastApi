import os
from datetime import datetime

import jwt
from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker

from auth.jwt_token import SECRET_KEY, create_access_token, algorithm
from job.logger import debug
from job.models import User, engine
from passlib.context import CryptContext
from pydantic import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    captcha: str

    def hash_password(self):
        self.password = pwd_context.hash(self.password)
        return self


def create_super_user(username='admin', password='password', email='admin@example.com'):
    _session = sessionmaker(bind=engine)
    session = _session()
    hashed_password = pwd_context.hash(password)
    admin = User(username=username, password=hashed_password, email=email, is_superuser=True)
    session.add(admin)
    session.commit()
    session.close()


def get_user(username: str) -> User:
    _session = sessionmaker(bind=engine)
    session = _session()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=algorithm)
        username = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired authentication credentials")

    # Check if token has expired
    token_exp = payload.get("exp")
    debug(f"f: get_current_user, token_exp (type): {datetime.utcfromtimestamp(token_exp)}, dt: {datetime.utcnow()}")
    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # for debugging:
    debug(f'Refresh last {os.environ.get("TOKEN_REFRESH_LAST_MINUTES")} minutes before expiring')
    token_need_update_str = datetime.utcfromtimestamp(token_exp - (60 * int(os.environ.get('TOKEN_REFRESH_LAST_MINUTES')))).strftime("%Y-%m-%d %H:%M:%S")
    token_exp_str = datetime.utcfromtimestamp(token_exp).strftime("%Y-%m-%d %H:%M:%S")
    debug(f'Update at: {token_need_update_str}, exp: {token_exp_str}')

    if token_exp is None or (
            datetime.utcfromtimestamp(token_exp - (60 * int(os.environ.get('TOKEN_REFRESH_LAST_MINUTES')))) <
            datetime.utcnow() <
            datetime.utcfromtimestamp(token_exp)
    ):
        # Need to generate a new access token if token has expired
        user.need_refresh_token = True
    return user


def refresh_token_if_need(response: dict, current_user: User) -> dict:
    if current_user.need_refresh_token:
        # Generate a new token with a new expiration time
        jwt_token = create_access_token(data={"username": current_user.username})
        response["access_token"] = jwt_token
    return response


if __name__ == '__main__':
    create_super_user()
