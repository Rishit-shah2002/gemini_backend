from fastapi import APIRouter, Request, Header, HTTPException
import stripe
import os
from app.db.database import SessionLocal
from app.db.models import User

router = APIRouter(prefix="/webhook", tags=["Stripe Webhook"])

@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]

        db = SessionLocal()
        user = db.query(User).filter_by(id=user_id).first()
        if user:
            user.subscription_tier = "Pro"
            db.commit()
        db.close()

    return {"status": "success"}
