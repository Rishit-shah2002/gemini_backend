### File: `app/api/auth.py`
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import random

from app.db.database import get_db
from app.db import models
from app.core.config import settings

# JWT Settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

# Schemas
class SignupRequest(BaseModel):
    phone: str

class SendOtpRequest(BaseModel):
    phone: str

class VerifyOtpRequest(BaseModel):
    phone: str
    otp: str

class ForgotPasswordRequest(BaseModel):
    phone: str

class ChangePasswordRequest(BaseModel):
    new_password: str

# Auth Endpoints
@auth_router.post("/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(phone=payload.phone).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = models.User(phone=payload.phone)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@auth_router.post("/send-otp")
def send_otp(payload: SendOtpRequest, db: Session = Depends(get_db)):
    otp = generate_otp()
    user = db.query(models.User).filter_by(phone=payload.phone).first()

    if not user:
        user = models.User(phone=payload.phone, otp=otp)
        db.add(user)
    else:
        user.otp = otp
    db.commit()

    return {"message": "OTP sent successfully (mock)", "otp": otp}

@auth_router.post("/verify-otp")
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(phone=payload.phone, otp=payload.otp).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    user.is_verified = True
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(phone=payload.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    user.otp = otp
    db.commit()
    return {"message": "OTP sent for password reset", "otp": otp}

@auth_router.post("/change-password")
def change_password(payload: ChangePasswordRequest, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id  # set by middleware
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = payload.new_password  # store securely in production
    db.commit()
    return {"message": "Password updated successfully"}

@auth_router.get("/me")
def get_current_user(request: Request, db: Session = Depends(get_db)):  
    user_id = request.state.user_id
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"phone": user.phone, "is_verified": user.is_verified}
