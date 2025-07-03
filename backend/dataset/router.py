from fastapi import APIRouter, UploadFile, File, HTTPException
from dataset.services import handle_upload, get_all_datasets, get_dataset_images

router = APIRouter()


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    return await handle_upload(file)

@router.get("/")
async def list_datasets():
    return await get_all_datasets()

@router.get("/{dataset_name}/images")
async def get_images(dataset_name: str):
    images = await get_dataset_images(dataset_name)
    if images is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return images