from fastapi import FastAPI
import os
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from bson import ObjectId
app = FastAPI

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")


class UrlCreate(BaseModel):
    original_url: HttpUrl

class UrlUpdate(BaseModel):
    original_url: HttpUrl

class UrlResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    access_count: int
    access_times: list[datetime]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }


