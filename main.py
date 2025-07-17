
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel, HttpUrl
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import shortuuid
from datetime import datetime
import os

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client.url_shortener
urls_collection = db.urls

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
            return short_code

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

@app.get("/api/urls/{short_code}/stats", response_model=UrlResponse)
async def get_url_stats(short_code: str):
    url_data = await urls_collection.find_one({"short_code": short_code})
    if not url_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")
    return url_data

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>URL Shortener</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 flex items-center justify-center h-screen">
        <div class="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
            <h1 class="text-2xl font-bold mb-4 text-center">URL Shortener</h1>
            <div class="mb-4">
                <input type="url" id="urlInput" class="w-full p-2 border rounded" placeholder="Enter URL to shorten">
            </div>
            <button onclick="shortenUrl()" class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600">Shorten URL</button>
            <div id="result" class="mt-4"></div>
        </div>
        <script>
            async function shortenUrl() {
                const url = document.getElementById('urlInput').value;
                try {
                    const response = await fetch('/api/urls', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ original_url: url })
                    });
                    const data = await response.json();
                    if (response.ok) {
                        const shortUrl = `${window.location.origin}/${data.short_code}`;
                        document.getElementById('result').innerHTML = `
                            <p>Short URL: <a href="${shortUrl}" class="text-blue-500">${shortUrl}</a></p>
                            <p>Original URL: ${data.original_url}</p>
                            <p>Access Count: ${data.access_count}</p>
                            <p>Access Times: ${data.access_times.join(', ')}</p>
                        `;
                    } else {
                        document.getElementById('result').innerHTML = `<p class="text-red-500">${data.detail}</p>`;
                    }
                } catch (error) {
                    document.getElementById('result').innerHTML = `<p class="text-red-500">Error: ${error.message}</p>`;
                }
            }
        </script>
    </body>
    </html>
    """
