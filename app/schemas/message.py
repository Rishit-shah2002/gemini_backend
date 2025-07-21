from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: int
    content: str
    is_user: bool
    created_at: datetime

    class Config:
        from_attributes = True
