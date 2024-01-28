from fastapi import Depends, HTTPException, Request
import jwt
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

async def getCurrentUserData(request: Request):
    token = request.cookies.get("accessToken")
    if token is None:
        raise HTTPException(status_code=401, detail="Token not found in cookie")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token")

def hashPassword(password: str) -> str:
    salt = bcrypt.gensalt()
    hashedPassword = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashedPassword.decode('utf-8')