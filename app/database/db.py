from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI

client = None
db = None

async def init_db(app: FastAPI):
    global client, db
    client = AsyncIOMotorClient("mongodb:://localhost:2701")
    db = client["url_shortener"]
    print("MongoDb connected")

async def close_db(app: FastAPI):
    client.close()
    print("MongoDB connection closed")

