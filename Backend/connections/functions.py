from fastapi import APIRouter
from fastapi import FastAPI, Response, Request, Depends, Form
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi import *
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import pandas as pd
import torch
from torch_snippets import *


class Register(BaseModel):
    username: str
    email: str
    password: str

class Login(BaseModel):
    username: str
    password: str

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
    
