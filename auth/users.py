import jwt
from fastapi import HTTPException, Header
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth.jwt_token import SECRET_KEY
from job.models import User, engine
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_super_user(username='admin', password='password', email='admin@example.com'):
    _session = sessionmaker(bind=engine)
    session = _session()
    hashed_password = pwd_context.hash(password)
    admin = User(username=username, password=hashed_password, email=email, is_superuser=True)
    session.add(admin)
    session.commit()


def get_user(username: str) -> User:
    _session = sessionmaker(bind=engine)
    session = _session()
    user = session.query(User).filter_by(username=username).first()
    return user


async def get_current_user(token: str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return user

if __name__ == '__main__':
    create_super_user()
