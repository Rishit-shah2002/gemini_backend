from fastapi import FastAPI
from app.api import auth, chatroom, subscription, webhook
from app.middleware.auth_middleware import JWTMiddleware

app = FastAPI()

from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
load_dotenv()

# Optional: Customize OpenAPI schema to include Bearer auth globally
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Gemini Chat API",
        version="1.0.0",
        description="Backend for Gemini-style chat platform",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.add_middleware(JWTMiddleware)

app.include_router(subscription.subscription_router)
app.include_router(webhook.webhook_router)
app.include_router(auth.auth_router)
app.include_router(chatroom.chat_router)

from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)