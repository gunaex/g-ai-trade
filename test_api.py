from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI
app = FastAPI(
    title="Test API",
    version="1.0.0",
    description="Test API"
)

class TestRequest(BaseModel):
    name: str
    value: Optional[float] = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test/{name}")
async def test(name: str):
    return {"name": name}