import os, shutil, zipfile, json, aiofiles
from utils.yolo import validate_yolo_structure, parse_labels
from utils.file_processing import extract_zip_async
from dataset.models import DatasetInDB
from datetime import datetime
from pymongo import MongoClient
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from bson.json_util import dumps
import uuid
from math import ceil

from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.yolo
dataset_collection = db.datasets

async def handle_upload(file):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported.")

    unique_id = str(uuid.uuid4())
    dataset_path = f"datasets/{unique_id}"
    os.makedirs(dataset_path, exist_ok=True)

    zip_path = os.path.join(dataset_path, file.filename)
    async with aiofiles.open(zip_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    try:
        folder_path = await extract_zip_async(zip_path, dataset_path)
        validate_yolo_structure(folder_path)
        images, labels = parse_labels(folder_path, file.filename.replace(".zip", ""))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    dataset_collection.insert_one({
        "name": file.filename.replace(".zip", ""),
        "status": "completed",
        "created_at": datetime.utcnow(),
        "total_images": len(images),
        "images": labels
    })

    shutil.rmtree(dataset_path)

    return {"message": "Upload successful"}

async def get_all_datasets():
    datasets_cursor = dataset_collection.find({}, {"images": 0})
    datasets = await datasets_cursor.to_list(length=100)  # control max returned items
    return JSONResponse(content=json.loads(dumps(datasets)))


async def get_dataset_images(dataset_name, page: int, page_size: int = 20):
    dataset = await dataset_collection.find_one({"name": dataset_name})
    if not dataset:
        return None

    images_dict = dataset.get("images", {})
    image_items = list(images_dict.items())

    total_images = len(image_items)
    total_pages = ceil(total_images / page_size)

    # Handle page out of range
    if page > total_pages and total_pages > 0:
        raise HTTPException(status_code=400, detail=f"Page {page} out of range. Total pages: {total_pages}")

    start = (page - 1) * page_size
    end = start + page_size
    paginated_images = image_items[start:end]

    images_array = [
        {"image_name": name, "labels": labels}
        for name, labels in paginated_images
    ]

    return {
        "images": images_array,
        "total_images": total_images,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size
    }