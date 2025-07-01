# app/routes/shipment_routes.py 
from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.models.shipment_models import Shipment
from app.utils.rbac import get_current_user, is_admin
from app.db.mongodb import db
from bson import ObjectId
from typing import List

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Create shipment form 
@router.get("/create", response_class=HTMLResponse, tags=["Shipments"])
async def create_shipment_form(request: Request, user=Depends(get_current_user)): 
    return templates.TemplateResponse("create_shipment.html", {"request": request, "user": user}) 

# Create shipment submission 
@router.post("/shipment", response_class=HTMLResponse, tags=["Shipments"])
async def create_shipment(request: Request, user=Depends(get_current_user),
                          shipmentNumber: str = Form(...),
                          routeDetails: str = Form(...),
                          device: str = Form(...),
                          poNumber: str = Form(...),
                          ndcNumber: str = Form(...),
                          serialNumberOfGoods: str = Form(...),
                          containerNumber: str = Form(...),
                          goodsType: str = Form(...),
                          expectedDeliveryDate: str = Form(...),
                          deliveryNumber: str = Form(...),
                          batchNumber: str = Form(...),
                          shipmentDescription: str = Form(...)): 

    shipment = Shipment(
        shipmentNumber=shipmentNumber, routeDetails=routeDetails, device=device,
        poNumber=poNumber, ndcNumber=ndcNumber, serialNumberOfGoods=serialNumberOfGoods,
        containerNumber=containerNumber, goodsType=goodsType,
        expectedDeliveryDate=expectedDeliveryDate, deliveryNumber=deliveryNumber,
        batchNumber=batchNumber, shipmentDescription=shipmentDescription
    ) 
    
    # Add the creator's username to the shipment data
    shipment_data = shipment.model_dump()
    shipment_data["createdBy"] = user.get("sub") # 'sub' typically holds the username from the token

    await db.shipments.insert_one(shipment_data) 
    
    redirect_url = "/admin/dashboard" if user["role"] == "admin" else "/user/dashboard" 
    return RedirectResponse(url=f"{redirect_url}?msg=Shipment+created+successfully",status_code=303) 

#edit shipment form 
@router.get("/edit/{shipment_id}", response_class=HTMLResponse, tags=["Shipments"])
async def edit_shipment_form(request: Request, shipment_id: str, user=Depends(is_admin)): 
    shipment = await db.shipments.find_one({"_id": ObjectId(shipment_id)}) 
    return templates.TemplateResponse("edit_shipment.html", {"request": request, "shipment": shipment, "shipment_id": shipment_id}) 

# update shipment 
@router.post("/edit/{shipment_id}", response_class=HTMLResponse, tags=["Shipments"])
async def update_shipment(shipment_id: str, request: Request, user=Depends(is_admin),
                           shipmentNumber: str = Form(...), routeDetails: str = Form(...), device: str = Form(...),
                           poNumber: str = Form(...), ndcNumber: str = Form(...), serialNumberOfGoods: str = Form(...),
                           containerNumber: str = Form(...), goodsType: str = Form(...), expectedDeliveryDate: str = Form(...),
                           deliveryNumber: str = Form(...), batchNumber: str = Form(...), shipmentDescription: str = Form(...)): 

    shipment = Shipment(
        shipmentNumber=shipmentNumber, routeDetails=routeDetails, device=device,
        poNumber=poNumber, ndcNumber=ndcNumber, serialNumberOfGoods=serialNumberOfGoods,
        containerNumber=containerNumber, goodsType=goodsType,
        expectedDeliveryDate=expectedDeliveryDate, deliveryNumber=deliveryNumber,
        batchNumber=batchNumber, shipmentDescription=shipmentDescription
    ) 
    result = await db.shipments.update_one({"_id": ObjectId(shipment_id)}, {"$set": shipment.model_dump()}) 
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Shipment not found or data was not changed") 
    return RedirectResponse(url="/admin/dashboard?msg=Shipment+updated+successfully", status_code=303) 


# FRONTEND ROUTE 
@router.get("/manage", response_class=HTMLResponse, include_in_schema=False)
async def manage_shipments_page(request: Request, user=Depends(is_admin)): 
    shipments = await db.shipments.find().to_list(length=100) 
    return templates.TemplateResponse("manage_shipments.html", {"request": request, "shipments": shipments}) 


# API ROUTE FOR SWAGGER
@router.get("/manage/api", response_model=List[Shipment], tags=["Shipments"])
async def manage_shipments_api(user=Depends(is_admin)):
    shipments = []
    for doc in await db.shipments.find().to_list(length=None):
        doc["id"] = str(doc["_id"])
        shipments.append(doc)
    return shipments