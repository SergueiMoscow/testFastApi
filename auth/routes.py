import os

import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasicCredentials
from fastapi.responses import Response

from auth.captcha import generate_captcha
from auth.users import get_user, get_current_user, refresh_token_if_need
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


# @app.post("/register")
# def register_user(user: User):
#     debug(f"Registering user {user.username}")
    # save_user(user)
    # return {"message": "User created"}


@router.get("/protected")
async def protected_route(current_user=Depends(get_current_user)):
    result = {"message": "This is a protected route.", "user": current_user.username, "email": current_user.email}
    return refresh_token_if_need(result, current_user)

