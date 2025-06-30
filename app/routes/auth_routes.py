# app/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends, Response, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from passlib.context import CryptContext
from app.db.mongodb import db
from app.utils.auth import create_access_token
from app.utils.rbac import get_current_user
from fastapi.templating import Jinja2Templates
import os
import httpx
import re 


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, msg: str = ""):
    site_key = os.getenv("RECAPTCHA_SITE_KEY")
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg, "recaptcha_site_key": site_key})


# Login handler (POST) for frontend forms
@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...), g_recaptcha_response: str = Form(alias="g-recaptcha-response")):
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY")
    async with httpx.AsyncClient() as client:
        verify = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": secret_key,
                "response": g_recaptcha_response
            }
        )
        result = verify.json()
        if not result.get("success"):
            return templates.TemplateResponse("login.html", {
                "request": request,
                "msg": "Captcha verification failed.",
                "recaptcha_site_key": os.getenv("RECAPTCHA_SITE_KEY")
            }, status_code=400)
    db_user = await db.users.find_one({"username": username})
    if not db_user or not pwd_context.verify(password, db_user["password"]):
        return templates.TemplateResponse("login.html", {
        "request": request,
        "msg": "Invalid username or password",
        "recaptcha_site_key": os.getenv("RECAPTCHA_SITE_KEY")
    }, status_code=401)

    token = create_access_token({"sub": db_user["username"], "role": db_user["role"]})
    response = RedirectResponse(url="/admin/dashboard" if db_user["role"] == "admin" else "/user/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=1800, samesite="lax", secure=False)
    return response

# Signup page (GET)
@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# Password validation function
def validate_password(password: str) -> str | None:
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    return None 

# Signup handler (POST)
@router.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if await db.users.find_one({"username": username}):
        return templates.TemplateResponse("signup.html", {"request": request,"error": "Username already exists"})
    if password != confirm_password:
        return templates.TemplateResponse("signup.html", {"request": request,"error": "Passwords do not match"})

    password_error = validate_password(password)
    if password_error:
        return templates.TemplateResponse("signup.html", {"request": request,"error": password_error})
    hashed_pw = pwd_context.hash(password)
    await db.users.insert_one({"username": username, "email": email, "password": hashed_pw, "role": "user"})
    return RedirectResponse(url="/auth/login?msg=Account created successfully. Please login.", status_code=303)

# Logout handler
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response

# API endpoint to get current user info from a token
@router.get("/me")
async def get_current_user_profile(user: dict = Depends(get_current_user)):
    return {"username": user["sub"], "role": user["role"]}

# API endpoint to get a token 
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await db.users.find_one({"username": form_data.username})
    if not db_user or not pwd_context.verify(form_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user["username"], "role": db_user["role"]})
    return {"access_token": token, "token_type": "bearer"}
