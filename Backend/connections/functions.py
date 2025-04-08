from dependencies.session import get_current_user
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import APIRouter, FastAPI, Response, Depends, Form, HTTPException, status
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path as FilePath
import bcrypt
from fastapi import *
from ultralytics import YOLO
from typing import Optional, Dict
import cv2
import matplotlib.pyplot as plt
import pandas as pd
import torch
from torch_snippets import *
import user_agents
import datetime
import secrets

class Register(BaseModel):
    username: str
    email: str
    password: str

class TherapistRegister(BaseModel):
    first_name: str
    last_name: str
    company_email: str
    password: str
class Login(BaseModel):
    username: str
    password: str
    remember_me: bool = False
    
class SessionData(BaseModel):
    user_id: int
    email: str
    expires: datetime.datetime

async def create_session(user_id: int, email: str, remember: bool = False) -> str:
    session_id = secrets.token_hex(16)
  

def serialize_document(doc):
    """Convert MongoDB document to a JSON-serializable format"""
    return {
        "id": str(doc["_id"]),
        "user_id": doc["user_id"],
        "image": doc["image"],
        "annotations": doc["annotations"],
        "size": doc["size"],
        "save_location": doc["save_location"],
        "model_used": doc["model_used"],
        "timestamp": doc["timestamp"].isoformat(),
        "status": doc["status"],
        "confidence_threshold": doc["confidence_threshold"],
        "processing_time": doc["processing_time"],
        "device": doc["device"]
    }
    
