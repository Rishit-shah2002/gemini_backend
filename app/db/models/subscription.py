from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    status = Column(String, default="basic")  # 'basic' or 'pro'
    created_at = Column(DateTime, default=datetime.utcnow)
    current_period_end = Column(DateTime)

    user = relationship("User", back_populates="subscription")
