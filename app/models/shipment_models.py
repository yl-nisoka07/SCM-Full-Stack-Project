# app/models/shipment_models.py
from pydantic import BaseModel

class Shipment(BaseModel):
    shipmentNumber: str
    routeDetails: str
    device: str
    poNumber: str
    ndcNumber: str
    serialNumberOfGoods: str
    containerNumber: str
    goodsType: str
    expectedDeliveryDate: str
    deliveryNumber: str
    batchNumber: str
    shipmentDescription: str
