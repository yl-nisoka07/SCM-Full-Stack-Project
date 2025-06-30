# app/models/user_models.py
from pydantic import BaseModel, EmailStr, validator
import re

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str

    @validator("password")
    def validate_password(cls, v):
        if (len(v) < 8 or not re.search(r"[A-Z]", v) or 
            not re.search(r"[0-9]", v) or not re.search(r"[^\w\s]", v)):
            raise ValueError("Password must be 8+ chars, contain 1 uppercase, 1 number, and 1 symbol")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"
