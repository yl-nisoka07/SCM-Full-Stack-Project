# app/routes/user_routes.py 
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.utils.rbac import is_admin, get_current_user
from app.db.mongodb import db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Admin dashboard 
@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, user=Depends(is_admin)):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "user": user})

# Admin: view all users 
@router.get("/admin/users", response_class=HTMLResponse)
async def list_users(request: Request, user=Depends(is_admin)):
    users = await db.users.find().to_list(100)
    return templates.TemplateResponse("user_list.html", {"request": request, "users": users})

# Form to update user role 
@router.get("/admin/edit-user", response_class=HTMLResponse)
async def edit_user_role_form(request: Request, user=Depends(is_admin)):
    return templates.TemplateResponse("edit_userdetails.html", {"request": request})

# Handler for updating user role from form 
@router.post("/admin/update-role")
async def update_user_role(username: str = Form(...), new_role: str = Form(...), user=Depends(is_admin)):
    result = await db.users.update_one(
        {"username": username},
        {"$set": {"role": new_role}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or role unchanged")
    return RedirectResponse(url="/admin/users?msg=Role+updated+successfully", status_code=303)


# User dashboard 
@router.get("/user/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("user_dashboard.html", {"request": request, "user": user})

# User profile/info page 
@router.get("/user/info", response_class=HTMLResponse)
async def user_info(request: Request, user=Depends(get_current_user)):
    db_user = await db.users.find_one({"username": user["sub"]})
    return templates.TemplateResponse("user_info.html", {"request": request, "user": user, "email": db_user["email"]})

# deleting a user from form 
@router.post("/admin/delete-user")
async def delete_user(username: str = Form(...), user=Depends(is_admin)):
    result = await db.users.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return RedirectResponse(url="/admin/users?msg=User+deleted+successfully", status_code=303)
