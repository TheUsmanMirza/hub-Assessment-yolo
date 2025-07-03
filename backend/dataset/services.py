import os, shutil, zipfile, json
from utils.yolo import parse_yolo_annotations
from dataset.models import DatasetInDB
from datetime import datetime
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from bson.json_util import dumps

client = MongoClient("mongodb://localhost:27017")
db = client.yolo
dataset_collection = db.datasets

async def handle_upload(file):
    filename = file.filename
    dataset_name = filename.rsplit(".", 1)[0]
    local_path = f"/tmp/{dataset_name}"
    zip_path = f"{local_path}.zip"

    with open(zip_path, "wb") as f:
        f.write(await file.read())

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(local_path)

    images = parse_yolo_annotations(local_path)

    # Store files locally instead of uploading to GCS
    storage_path = f"datasets/{dataset_name}"
    os.makedirs(storage_path, exist_ok=True)
    for root, _, files in os.walk(local_path):
        for file_name in files:
            src = os.path.join(root, file_name)
            dst = os.path.join(storage_path, os.path.relpath(src, local_path))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    dataset_collection.insert_one({
        "name": dataset_name,
        "status": "completed",
        "created_at": datetime.utcnow(),
        "total_images": len(images),
        "images": images
    })

    shutil.rmtree(local_path)
    os.remove(zip_path)

    return {"message": "Upload successful"}

async def get_all_datasets():


    datasets = dataset_collection.find({}, {"images": 0})
    return JSONResponse(content=json.loads(dumps(datasets)))

async def get_dataset_images(dataset_name):
    dataset = dataset_collection.find_one({"name": dataset_name})
    if not dataset:
        return None
    return dataset.get("images", [])