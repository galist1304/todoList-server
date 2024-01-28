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

            # Check if the userId exists in the database
            if db.users.find_one({'_id': ObjectId(task.taskForUser)}):
                task.userID = task.taskForUser
            else:
                raise HTTPException(status_code=400, detail="Invalid userID")
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
async def getTasks(status: str = None, payload: dict = Depends(getCurrentUserData)):
    try:
        statusFilter : dict = {}

        # Check if a query is passed
        if status != None:
            statusFilter['status'] = status
        if payload['role'] == 'admin':
            tasks = db.tasks.find(statusFilter)
        else:
            statusFilter['userID'] = payload['userID']
            tasks = db.tasks.find(statusFilter)
        taskList = [task for task in tasks]
        for task in taskList:
            task['_id'] = str(task['_id'])
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

