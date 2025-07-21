from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import Chatroom  # Use PascalCase model name
from app.db.database import get_db
from app.schemas.chatroom import ChatroomCreate, ChatroomOut
from redis import Redis
from rq import Queue
from app.tasks.gemini_task import generate_gemini_reply
from app.schemas.message import MessageCreate, MessageOut
from app.db.models.message import Message 
from app.db.models import User
from datetime import datetime
from fastapi.responses import JSONResponse

chat_router = APIRouter(prefix="/chatroom", tags=["Chatroom"])


queue = Queue(connection=Redis())
r = redis.Redis(host="localhost", port=6379, db=0)

DAILY_LIMIT = 5  # Basic tier limit

@chat_router.post("/{chatroom_id}/message", response_model=MessageOut)
def send_message(chatroom_id: int, message_data: MessageCreate, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id

    # Check user subscription
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Rate limit only Basic users
    if user.subscription_tier == "Basic":
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        redis_key = f"rate_limit:{user_id}:{today_str}"

        current_count = int(r.get(redis_key) or 0)

        if current_count >= DAILY_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"success": False, "error": "Daily message limit exceeded for Basic tier. Upgrade to Pro."}
            )

        # Increment counter with 24h TTL if key is new
        if current_count == 0:
            r.set(redis_key, 1, ex=86400)
        else:
            r.incr(redis_key)

    chatroom = db.query(Chatroom).filter_by(id=chatroom_id, owner_id=user_id).first()
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chatroom not found")

    # Store user message
    user_msg = Message(
        content=message_data.content,
        is_user=True,
        chatroom_id=chatroom_id
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Queue Gemini response
    queue.enqueue(generate_gemini_reply, chatroom_id, message_data.content)

    return user_msg

# ✅ POST /chatroom - Create a new chatroom
@chat_router.post("/", response_model=ChatroomOut, status_code=status.HTTP_201_CREATED)
def create_chatroom(chatroom_data: ChatroomCreate, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    new_chatroom = Chatroom(name=chatroom_data.name, owner_id=user_id)
    db.add(new_chatroom)
    db.commit()
    db.refresh(new_chatroom)
    return new_chatroom

# ✅ GET /chatroom - List all chatrooms for the user
@chat_router.get("/", response_model=list[ChatroomOut])
def list_chatrooms(request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    chatrooms = db.query(Chatroom).filter_by(owner_id=user_id).all()
    return chatrooms

# ✅ GET /chatroom/{chatroom_id} - Get a specific chatroom
@chat_router.get("/{chatroom_id}", response_model=ChatroomOut)
def get_chatroom(chatroom_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.state.user_id
    chat = db.query(Chatroom).filter_by(id=chatroom_id, owner_id=user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chatroom not found")
    return chat
