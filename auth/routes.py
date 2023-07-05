import os

import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasicCredentials
from fastapi.responses import Response

from auth.captcha import generate_captcha
from auth.users import get_user, get_current_user, refresh_token_if_need, UserCreate
from auth.jwt_token import create_access_token, pwd_context
from job.logger import debug
from job.models import User
from captcha.image import ImageCaptcha
from io import BytesIO

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


@router.post("/login")
def login(credentials: HTTPBasicCredentials):
    user = get_user(credentials.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not pwd_context.verify(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    jwt_token = create_access_token(data={"username": user.username})
    return {"access_token": jwt_token}


@router.get("/captcha")
async def get_captcha():
    captcha_text, image_buffer = generate_captcha()
    response = Response(content=image_buffer.getvalue(), media_type="image/png")
    response.headers["token"] = create_access_token({'captcha-text': captcha_text})
    return response


async def get_headers(request: Request):
    return request.headers


@router.post("/register")
async def register_user(create_user: UserCreate, headers: dict = Depends(get_headers)):
    captcha_encrypted = headers.get('token')
    if not captcha_encrypted:
        raise HTTPException(status_code=401, detail="Missing captcha")
    captcha_text = jwt.decode(captcha_encrypted, options={"verify_signature": False})['captcha-text']
    if captcha_text != create_user.captcha:
        raise HTTPException(status_code=401, detail="Invalid captcha")
    debug(f"Create user {create_user}")
    create_user.hash_password()
    user = get_user(create_user.username)
    debug(f"User {user}")
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    user_dict = create_user.dict()
    user_dict["is_superuser"] = False

    del user_dict["captcha"]
    debug(f"Dict user {user_dict}")
    user = User(**user_dict)
    user.save()
    return {"message": "User created successfully"}


@router.get("/protected")
async def protected_route(current_user=Depends(get_current_user)):
    result = {"message": "This is a protected route.", "user": current_user.username, "email": current_user.email}
    return refresh_token_if_need(result, current_user)

