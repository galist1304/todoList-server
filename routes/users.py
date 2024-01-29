from fastapi import APIRouter, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from utils import hashPassword, getCurrentUserData
from models.userModel import User, createAccessToken
from database import db
from datetime import datetime

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
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

# Login route
@router.post("/")
async def login(user: User, response: Response):
    try:

        # check if the username exists in the database
        if db.users.find_one({"username": user.username}):
            userData = db.users.find_one({"username": user.username})

            # create the access token
            accessToken = createAccessToken(data={"userID": str(userData['_id']), "role": str(userData['role'])})

            # set the access token in a cookie
            response.set_cookie(key="accessToken", value=accessToken, max_age=3600, httponly=True, secure=True, samesite='none')
            return {"message": "Access token updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="User not found")

    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tokenData")
async def getTokenData(payload: dict = Depends(getCurrentUserData)):
    try:
        return {"userData": payload}
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")  
async def logout(response: Response):
    response.delete_cookie("accessToken")
    return {"message": "Cookie deleted successfully"}
