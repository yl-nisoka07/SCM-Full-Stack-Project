# app/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from app.routes import auth_routes, shipment_routes, device_routes, user_routes
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SCMXpertLite API",description="API for SCM")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401 and "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url="/auth/login?msg=Please login to continue", status_code=303)
    
    # else return JSON
    return JSONResponse(status_code=exc.status_code,content={"detail": exc.detail},headers=exc.headers)

app.include_router(auth_routes.router, prefix="/auth",tags=["Authentication"])
app.include_router(shipment_routes.router, prefix="/shipment", tags=["Shipments"])
app.include_router(device_routes.router, prefix="/device", tags=["Devices"])
app.include_router(user_routes.router, tags=["Users & Dashboards"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/auth/login")

app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"],)
