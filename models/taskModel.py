from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Task(BaseModel):
    text : str
    status : str
    userID : Optional[str] = None
    created_at: datetime = None
    taskForUser : Optional[str] = None

