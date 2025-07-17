from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel, HttpUrl
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import shortuuid
from datetime import datetime
import os

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

async def generate_unique_short_code():
    while True:
        short_code = shortuuid.uuid()[:8]
        existing = await urls_collection.find_one({"short_code": short_code})
        if not existing:
            return 
        
@app.post("/api/urls", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
async def create_short_url(url: UrlCreate):
    short_code = await generate_unique_short_code()
    url_data = {
        "short_code": short_code,
        "original_url": str(url.original_url),
        "created_at": datetime.utcnow(),
        "access_count": 0,
        "access_times": []
    }
    result = await urls_collection.insert_one(url_data)
    return {**url_data, "_id": str(result.inserted_id)}

@app.get("/{short_code}", response_class=RedirectResponse)
async def redirect_to_original_url(short_code: str):
    url_data = await urls_collection.find_one({"short_code": short_code})
    if not url_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    
    await urls_collection.update_one(
        {"short_code": short_code},
        {
            "$inc": {"access_count": 1},
            "$push": {"access_times": datetime.utcnow()}
        }
    )
    return url_data["original_url"]

@app.put("/api/urls/{short_code}", response_model=UrlResponse)
async def update_short_url(short_code: str, url: UrlUpdate):
    url_data = await urls_collection.find_one({"short_code": short_code})
    if not url_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    
    updated_data = {
        "original_url": str(url.original_url),
        "updated_at": datetime.utcnow()
    }
    await urls_collection.update_one(
        {"short_code": short_code},
        {"$set": updated_data}
    )
    updated_url = await urls_collection.find_one({"short_code": short_code})
    return updated_url

@app.delete("/api/urls/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url(short_code: str):
    result = await urls_collection.delete_one({"short_code": short_code})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    return None

