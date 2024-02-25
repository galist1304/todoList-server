from fastapi import APIRouter, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from utils import hashPassword, getCurrentUserData, verifyPassword, decodeToken, getRefreshTokenData
from models.userModel import User, createAccessToken, createRefreshToken
from database import db
from datetime import datetime
import base64
from bson import ObjectId
import re
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

router = APIRouter(prefix = '/users', tags = ['users'])

@router.post("/googleLogin")
async def googleLogin(user: User, response: Response):
    try:
        user.created_at = datetime.now()
        if not db.users.find_one({'username': user.username}):
            db.users.insert_one(user.dict())
        userData = db.users.find_one({'username': user.username})
        userData["_id"] = str(userData["_id"])
        if userData:    
            accessToken = createAccessToken(data={"userID": userData['_id'], "role": userData['role']})
            refreshToken = createRefreshToken(data={"userID": userData['_id'], "role": userData['role']})
            response.set_cookie(key="accessToken", value=accessToken, max_age=3600, httponly=True, secure=True, samesite='none')
            response.set_cookie(key="refreshToken", value=refreshToken, max_age=3600, httponly=True, secure=True, samesite='none')
            return {'userData': userData}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

# Add a user to the database
@router.post("/signup")
async def addUser(user: User):
    try:
        user.created_at = datetime.now()
        hashedPassword = hashPassword(user.password)
        user.password = hashedPassword

        # set role to admin or user
        if user.username == "galist":
            user.role = "admin"
        else: 
            user.role = "user"
        
        db.users.insert_one(user.dict())
        userData = db.users.find_one({"username": user.username})
        return {"message": "User created successfully"}

    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

# Login route
@router.post('/login/token')
async def loginForAccessToken(response: Response, user: OAuth2PasswordRequestForm = Depends()):
    try:
        decodedData = base64.b64decode(user.password).decode("utf-8")
        user.password = decodedData
        userData = db.users.find_one({"username": user.username})
        if not userData:
            raise HTTPException(status_code=401, detail="Username or password are incorrect")
        if verifyPassword(userData["password"], user.password):
            accessToken = createAccessToken(data={"userID": str(userData['_id']), "role": str(userData['role'])})
            refreshToken = createRefreshToken(data={"userID": str(userData['_id']), "role": str(userData['role'])})
            response.set_cookie(key="accessToken", value=accessToken, max_age=3600, httponly=True, secure=True, samesite='none')
            response.set_cookie(key="refreshToken", value=refreshToken, max_age=3600, httponly=True, secure=True, samesite='none')
        else:
            raise HTTPException(status_code=401, detail="Username or password are incorrect")
        return {'message': 'Access and refresh tokens are set in cookie'}
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

# Refresh the access token
@router.post('/refresh')
async def refreshAccessToken(response: Response, payload: dict = Depends(getRefreshTokenData)):
    try:
        print(payload)
        userID = payload['userID']
        print(userID)
        if userID is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        userData = db.users.find_one({"_id": ObjectId(userID)})
        print(userData)
        if not userData:
            raise HTTPException(status_code=401, detail="User not found")
        accessToken = createAccessToken(data={"userID": str(userData['_id']), "role": str(userData['role'])})
        response.set_cookie(key="accessToken", value=accessToken, max_age=3600, httponly=True, secure=True, samesite='none')
        return {'message': 'Access token refreshed successfully'}
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))
        
@router.get('/usersList/')
async def usersList(search: str, payload: dict = Depends(getCurrentUserData)):
    try:
        if len(search) > 0:
            regex = re.compile(search, re.IGNORECASE)
            users = db.users.find({"username": {"$regex": regex}})
            usersList = [user for user in users]
            for user in usersList:
                user['_id'] = str(user['_id'])
            return {"usersList": usersList}
        else:
            raise HTTPException(status_code=400, detail="The search must be one characters at least")
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/userdata/{userID}")
async def userData(userID: str, payload: dict = Depends(getCurrentUserData)):
    try:
        userID = ObjectId(userID)
        user = db.users.find_one({"_id": userID})
        userList = [user]
        for user in userList:
            user['_id'] = str(user['_id'])
        if user:
            return {"userData": userList}   
        else: 
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tokenData")
async def getTokenData(payload: dict = Depends(getCurrentUserData)):
    try:
        return {"userData": payload}
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/logout")  
async def logout(response: Response):
    response.delete_cookie("accessToken")
    response.delete_cookie("refreshToken")
    return {"message": "Cookies deleted successfully"}
