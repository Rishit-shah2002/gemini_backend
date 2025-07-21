from app.db.database import SessionLocal
from app.db.models.message import Message
from app.utils.gemini_api import get_gemini_response  # Assume this exists

def generate_gemini_reply(chatroom_id: int, user_message: str):
    db = SessionLocal()
    try:
        reply = get_gemini_response(user_message)  # You handle actual Gemini API here
        gemini_msg = Message(
            content=reply,
            is_user=False,
            chatroom_id=chatroom_id
        )
        db.add(gemini_msg)
        db.commit()
    finally:
        db.close()
