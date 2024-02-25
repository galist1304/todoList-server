from fastapi import Depends, HTTPException, Request
import jwt
import bcrypt
from dotenv import load_dotenv
import os
import base64


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
PEPPER = os.getenv("PEPPER")


async def getCurrentUserData(request: Request):
    token = request.cookies.get("accessToken")
    if token is None:
        raise HTTPException(status_code=401, detail="Token not found in cookie")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.exceptions.DecodeError as decode_error:
        raise HTTPException(status_code=401, detail="Invalid token format: Not enough segments") from decode_error

async def getRefreshTokenData(request: Request):
    token = request.cookies.get("refreshToken")
    if token is None:
        raise HTTPException(status_code=401, detail="Token not found in cookie")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.exceptions.DecodeError as decode_error:
        raise HTTPException(status_code=401, detail="Invalid token format: Not enough segments") from decode_error

def hashPassword(password: str) -> str:
    decodedData = base64.b64decode(password).decode("utf-8")
    if len(decodedData) >= 3 and len(decodedData) <= 16:
        pepperedPassword = decodedData + PEPPER
        salt = bcrypt.gensalt()
        hashedPassword = bcrypt.hashpw(pepperedPassword.encode('utf-8'), salt)
        print(pepperedPassword)
        return hashedPassword.decode('utf-8')
    else:
        raise HTTPException(status_code=401, detail="Password must be between 3 and 16 characters")

def verifyPassword(hashedPassword, plainPassword):
    try:
        pepperedPassword = plainPassword + PEPPER
        return bcrypt.checkpw(pepperedPassword.encode('utf-8'), hashedPassword.encode('utf-8'))
    except Exception as e:
        print("Error:", str(e))
        return False  

def decodeToken(refreshToken):
    try:
        payload = jwt.decode(refreshToken, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.exceptions.DecodeError as decode_error:
        raise HTTPException(status_code=401, detail="Invalid token format: Not enough segments") from decode_error