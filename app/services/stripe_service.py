import os
import stripe
from app.models.user import User
from app.db.database import SessionLocal

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

DOMAIN = os.getenv("FRONTEND_URL", "http://localhost:3000")

def create_checkout_session(user: User):
    checkout_session = stripe.checkout.Session.create(
        success_url=f"{DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{DOMAIN}/cancel",
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price": os.getenv("STRIPE_PRICE_ID"),
            "quantity": 1,
        }],
        metadata={"user_id": user.id},
    )
    return checkout_session.url


def get_subscription_status(user: User):
    return {"subscription": user.subscription_tier or "Basic"}
