from fastapi import APIRouter, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from utils import hashPassword, getCurrentUserData, verifyPassword
from models.userModel import User, createAccessToken
from database import db
from datetime import datetime
import base64
from bson import ObjectId
import re


router = APIRouter(prefix = '/users', tags = ['users'])



# Add a user to the database
@router.post("/signup")
async def addUser(user: User, response: Response):
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

        # create the access token
        accessToken = createAccessToken(data={"userID": str(userData['_id']), "role": user.role})

        # set the access token in a cookie
        response.set_cookie(key="accessToken", value=accessToken, max_age=3600, httponly=True, secure=True, samesite='none')
        return {"message": "Access token updated successfully"}

    except Exception as e: 
        #print(e)
        raise HTTPException(status_code=400, detail=str(e))

# Login route
@router.post("/")
async def login(user: User, response: Response):
    try:
        decodedData = base64.b64decode(user.password).decode("utf-8")
        user.password = decodedData

        # check if the username exists in the database
        if db.users.find_one({"username": user.username}):
            userData = db.users.find_one({"username": user.username})
            if verifyPassword(userData['password'], user.password):
                # create the access token
                accessToken = createAccessToken(data={"userID": str(userData['_id']), "role": str(userData['role'])})

                # set the access token in a cookie
                response.set_cookie(key="accessToken", value=accessToken, max_age=3600, httponly=True, secure=True, samesite='none')
                return {"message": "Access token updated successfully"}
            else:
                raise HTTPException(status_code=400, detail="Username or password are incorrect")

            
        else:
            raise HTTPException(status_code=400, detail="Username or password are incorrect")

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
    return {"message": "Cookie deleted successfully"}
