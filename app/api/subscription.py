from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.services.stripe_service import create_checkout_session, get_subscription_status
from app.utils.auth import get_current_user

router = APIRouter(prefix="/subscribe", tags=["Subscription"])

@router.post("/pro")
def start_pro_subscription(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        session_url = create_checkout_session(user)
        return {"checkout_url": session_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
def subscription_status(user: User = Depends(get_current_user)):
    return get_subscription_status(user)
