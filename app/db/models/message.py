from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, default=True)  # True = user, False = Gemini
    created_at = Column(DateTime, default=datetime.utcnow)

    chatroom_id = Column(Integer, ForeignKey("chatrooms.id"))
    chatroom = relationship("Chatroom", back_populates="messages")
