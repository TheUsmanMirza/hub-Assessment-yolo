import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from dataset.services import handle_upload, get_all_datasets, get_dataset_images
from fastapi.responses import FileResponse

router = APIRouter()


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    return await handle_upload(file)

@router.get("/")
async def list_datasets():
    return await get_all_datasets()

@router.get("/{dataset_name}/images")
async def get_images(dataset_name: str, page: int = Query(1, ge=1)):
    images = await get_dataset_images(dataset_name, page)
    if images is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return images


@router.get("/{dataset_name}/image/{image_name}")
async def get_image_file(dataset_name: str, image_name: str):
    """Serve individual image files from the images directory structure"""
    # The main path where images are stored after processing
    main_path = f"datasets/images/{dataset_name}/{image_name}"

    if os.path.exists(main_path):
        return FileResponse(main_path)

    raise HTTPException(status_code=404, detail="Image not found")