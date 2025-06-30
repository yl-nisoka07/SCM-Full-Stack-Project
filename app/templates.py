# app/templates.py
from fastapi.templating import Jinja2Templates

# Point to the directory where your HTML files are located
templates = Jinja2Templates(directory="app/templates")