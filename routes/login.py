from datetime import datetime, timedelta
from typing import Annotated, List, Dict
from fastapi import Depends, APIRouter, Form, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt
from models.models import Token, TokenData, User, UserInDB, UserRegistration, News, myOpinion
from config.dbfull import get_database
from pymongo.collection import Collection

from schemas.schemas import UserPramuka

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

login = APIRouter(tags=["Login"])

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await get_user(username)  # Menambahkan kata kunci await di sini
        if user is None:
            raise credentials_exception
        return user
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
):
    user = current_user
    if not user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_news(
news : News = Depends(get_current_user)

):
    if not news.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return news

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(username: str):
    db = await get_database()
    user_dict = await db.users.find_one({"username": username})
    if user_dict:
        return UserInDB(**user_dict)
    else:
        return None

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def admin_required(current_user: UserInDB = Depends(get_current_user)):
    user = current_user
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    return current_user

# Decorator untuk memeriksa apakah pengguna adalah non-admin
def non_admin_required(current_user: UserInDB = Depends(get_current_user)):
    if current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    return current_user

@login.post("/register", response_model=Dict[str, str])
async def register_user(user: UserInDB, database=Depends(get_database)):
    db_users = database["users"]
    
    # Check if username already exists
    existing_username = await db_users.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check if email already exists
    existing_email = await db_users.find_one({"email": user.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password securely
    hashed_password = get_password_hash(user.hashed_password)

    # Create user dictionary
    user_dict = {
        "username": user.username,
        "full_name": user.full_name,
        'gudep_number': user.gudep_number,
        "email": user.email,
        "hashed_password": hashed_password,
        "active": user.active,
        "is_admin": False,
    }

    # Insert user into the database
    await db_users.insert_one(user_dict)

    return {"message": "User registered successfully"}

@login.post("/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    user = await authenticate_user(username, password)  # Menggunakan motor untuk authentikasi user
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@login.get("/users/me/")
async def read_users_me(
    current_user: UserInDB = Depends(get_current_user),
    database: Collection = Depends(get_database),
):
    db_opinion = database["opinion"]
    db_school = database["schools"]
    opinions_cursor = db_opinion.find({"sender_name": current_user.full_name})
    gudep_cursor = db_school.find({"gudep": current_user.gudep_number})

    opinions = []
    async for opinion in opinions_cursor:
        # Convert ObjectId to string
        if "_id" in opinion:
            opinion["_id"] = str(opinion["_id"])
        opinions.append(opinion)
    
    schools = []
    async for school in gudep_cursor:
        # Convert ObjectId to string
        if "_id" in school:
            school["_id"] = str(school["_id"])
        schools.append(school)

    user_with_opinions = {
        "full_name": current_user.full_name,
        "gudep_number": current_user.gudep_number,
        "email": current_user.email,
        "school": schools,
        "opinions": opinions,
    }
    
    return JSONResponse(user_with_opinions)

@login.get('/user/all',dependencies=[Depends(admin_required)])
async def get_all_user(database=Depends(get_database)):
    db_users = database["users"]
    user_cursor = db_users.find()
    user_list = await user_cursor.to_list(length=None)
    for user in user_list:
        for user in user_list:
            user["_id"] = str(user["_id"])
            user.setdefault("status", False)
    result = [UserPramuka(user) for user in user_list]
    return result