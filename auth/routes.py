import os

import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasicCredentials

from auth.users import get_user, get_current_user, refresh_token_if_need
from auth.jwt_token import create_access_token, pwd_context

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login")
def login(credentials: HTTPBasicCredentials):
    user = get_user(credentials.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not pwd_context.verify(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    jwt_token = create_access_token(data={"username": user.username})
    return {"access_token": jwt_token}


@router.get("/protected")
async def protected_route(current_user=Depends(get_current_user)):
    result = {"message": "This is a protected route.", "user": current_user.username, "email": current_user.email}
    return refresh_token_if_need(result, current_user)

