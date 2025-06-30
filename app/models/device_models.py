# app/models/device_models.py
from pydantic import BaseModel
from datetime import datetime

class DeviceData(BaseModel):
    device_id: str
    battery_level: float
    sensor_temperature: float
    route_from: str
    route_to: str
    timestamp: datetime
