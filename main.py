from fastapi import FastAPI
import os
from pydantic import BaseModel, HttpUrl

app = FastAPI

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")


class UrlCreate(BaseModel):
    original_url: HttpUrl