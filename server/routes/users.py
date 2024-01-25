from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from utils import hashPassword
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
        response.set_cookie(key="accessToken", value=accessToken, max_age=3600)
        return {"accessToken": accessToken}

    except Exception as e: 
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
            response.set_cookie(key="accessToken", value=accessToken, max_age=3600)
            return {"accessToken": accessToken}
        else:
            raise HTTPException(status_code=400, detail="User not found")

    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))



