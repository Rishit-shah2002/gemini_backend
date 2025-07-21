from pydantic import BaseModel
from datetime import datetime

class ChatroomCreate(BaseModel):
    name: str

class ChatroomOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
