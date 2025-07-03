from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict

class ImageLabel(BaseModel):
    image_name: str
    labels: List[Dict]

class DatasetInDB(BaseModel):
    name: str
    status: str
    created_at: datetime
    total_images: int