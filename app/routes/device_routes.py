# app/routes/device_routes.py
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.models.device_models import DeviceData
from app.utils.rbac import is_admin
from app.db.mongodb import db
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from typing import Optional


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/device-data")
async def add_device_data_api(data: DeviceData, user=Depends(is_admin)):
    await db.device_data.insert_one(data.dict())
    return {"msg": "Device data added successfully"}

@router.get("/device-data")
async def get_all_device_data_api(
    user=Depends(is_admin), 
    device_id: Optional[str] = Query(None)
):
    # Build query filter
    query_filter = {}
    if device_id:
        query_filter["device_id"] = device_id
    
    data = await db.device_data.find(query_filter).to_list(None)
    for item in data:
        item["_id"] = str(item["_id"])
    return data

@router.get("/device-data-page", response_class=HTMLResponse)
async def view_device_data_page(
    request: Request, 
    user=Depends(is_admin),
    device_id: Optional[str] = Query(None)
):
    # Build query filter
    query_filter = {}
    if device_id:
        query_filter["device_id"] = device_id
    
    data = await db.device_data.find(query_filter).to_list(None)
    
    # Get unique device IDs for filter dropdown
    all_devices = await db.device_data.distinct("device_id")
    
    return templates.TemplateResponse("device_data.html", {
        "request": request, 
        "device_data": data,
        "all_devices": all_devices,
        "selected_device": device_id
    })

@router.websocket("/ws/device-stream")
async def device_data_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            fake_data = {"device": "DEV123", "status": "active"}  # example
            await websocket.send_json(fake_data)
            await asyncio.sleep(2)  # stream every 2 seconds
    except WebSocketDisconnect:
        print("Client disconnected")