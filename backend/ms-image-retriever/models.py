from pydantic import BaseModel
from typing import List

class ImageInfo(BaseModel):
    type: str
    id: int

class ImageCheckRequest(BaseModel):
    images: List[ImageInfo]

class ImageExistence(BaseModel):
    type: str
    id: int
    image_exist: bool

class ImageCheckResponse(BaseModel):
    results: List[ImageExistence]
