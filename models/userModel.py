from pydantic import BaseModel,constr
from typing import Optional
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import jwt



load_dotenv()

class User(BaseModel):
    username : constr(min_length=3, max_length=100)
    password: Optional[constr(min_length=3, max_length=16)] = None
    role : Optional[str] = None
    created_at: datetime = None

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_MINUTES = 1440

def createAccessToken(data: dict):
    toEncode = data.copy()
    expiration_time = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    toEncode["exp"] = expiration_time.timestamp()
    return jwt.encode(toEncode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)

def createRefreshToken(data: dict):
    toEncode = data.copy()
    expiration_time = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    toEncode["exp"] = expiration_time.timestamp()
    return jwt.encode(toEncode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)