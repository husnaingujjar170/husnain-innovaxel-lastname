from pydantic import BaseModel

class URLModel(BaseModel):
    original_url: str
    short_url: str
    access_count: int = 0