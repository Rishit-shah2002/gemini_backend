from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.core.config import settings

EXCLUDE_PATHS = [
    "/auth/signup",
    "/auth/send-otp",
    "/auth/verify-otp",
    "/auth/forgot-password",
    "/docs",
    "/openapi.json",
    "/redoc",
]

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDE_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid or missing token")

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            request.state.user_id = int(payload.get("sub"))
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        return await call_next(request)