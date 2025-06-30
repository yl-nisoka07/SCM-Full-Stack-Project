# app/utils/rbac.py

from fastapi import Request, HTTPException, Depends, status
from app.utils.auth import verify_token, oauth2_scheme_swagger
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme_swagger = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
#  Swagger UI and HTML frontend (cookie-based)
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme_swagger)):
    cookie_token = request.cookies.get("access_token")
    actual_token = cookie_token or token
    if not actual_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_token(actual_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

# Admin check using hybrid user
async def is_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
