from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    otp = Column(String, nullable=True)
    subscription_tier = Column(String, default="Basic")
    password = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    chatrooms = relationship("Chatroom", back_populates="owner")
    subscription = relationship("Subscription", back_populates="user", uselist=False)