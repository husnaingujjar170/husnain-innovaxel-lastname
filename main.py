from fastapi import FastAPI
import os
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from bson import ObjectId
from fastapi.responses import RedirectResponse, HTMLResponse
import shortuuid
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


