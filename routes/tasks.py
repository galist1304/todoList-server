from fastapi import APIRouter, HTTPException, Depends
from models.taskModel import Task
from utils import getCurrentUserData
from datetime import datetime
from database import db
from bson import ObjectId

router = APIRouter(prefix = '/tasks', tags = ['tasks'])

# Add a task to the database
@router.post("/")
async def addTask(task: Task, payload: dict = Depends(getCurrentUserData)):
    try:
        task.created_at = datetime.now()
        if payload['role'] == 'admin':
            # Check if the userID exists in the database
            if task.taskForUser: 
                if db.users.find_one({'username': task.taskForUser}):
                    user = db.users.find_one({'username': task.taskForUser})
                    task.userID = str(user['_id'])
                else:
                    raise HTTPException(status_code=400, detail="Invalid username")
            else: 
                task.userID = payload['userID']
        else:
            task.userID = payload['userID']
        taskDict = task.dict()
        taskDict.pop('taskForUser', None)
        db.tasks.insert_one(taskDict)
        return {"task" : task}
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

# Get the tasks from the database
@router.get("/")
async def getTasks(payload: dict = Depends(getCurrentUserData)):
    try:
        if payload['role'] == 'admin':
            tasks = db.tasks.find({})
        else:
            tasks = db.tasks.find({'userID': payload['userID']})
        users_cursor = db.users.find({})
        userList = [user for user in users_cursor]
        users_dict = {str(user["_id"]): {"username": user["username"]} for user in userList}
        taskList = [task for task in tasks]
        for task in taskList:
            task['_id'] = str(task['_id'])
            userID = task.get("userID")
            if userID in users_dict:
                task["username"] = users_dict[userID]["username"]
            else:
                task["username"] = ""
        return {"tasks": taskList}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete a task from the database by ID
@router.delete("/delete/{taskID}")
async def deleteTask(taskID: str, payload: dict = Depends(getCurrentUserData)):
    try:
        deletedTask = db.tasks.delete_one({"_id": ObjectId(taskID)})
        if deletedTask.deleted_count == 1:
            return {"message": "Task deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/deleteCompleted")
async def deleteCompleted(payload: dict = Depends(getCurrentUserData)):
    try:
        response = db.tasks.delete_many({'status': 'Completed'})
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

# Update the task by ID
@router.patch("/update/{taskID}")
async def updateTask(taskID : str, task: Task, payload: dict = Depends(getCurrentUserData)):
    try:
        taskID = ObjectId(taskID)
        newTask = {
            "$set": {
                "text": task.text,
                "status": task.status
            }
        }
        updatedTask = db.tasks.update_one({"_id": taskID}, newTask)
        if updatedTask.modified_count == 1:
            return {"message": "Task updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e: 
        raise HTTPException(status_code=400, detail=str(e))

