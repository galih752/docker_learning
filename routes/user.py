from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from models.models import UserRegistration
from config.dbfull import db
import hashlib
import hmac
from jose import jwt, JWTError
import base64
from datetime import datetime, timedelta
from bson import json_util

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

regist = APIRouter(tags=["Registrasi"])

def hash_password(password: str, secret_key: str) -> str:
    hashed = hmac.new(secret_key.encode('utf-8'), password.encode('utf-8'), hashlib.sha256)
    return base64.urlsafe_b64encode(hashed.digest()).decode('utf-8')

def authenticate_user(username: str, password: str):
    user = db.users.find_one({"username": username})
    if user and verify_password(password, user["hashed_password"]):
        return user
    else:
        return None

def verify_password(plain_password, hashed_password):
    return hashed_password == hash_password(plain_password, SECRET_KEY)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")