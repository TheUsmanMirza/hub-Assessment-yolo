from fastapi import FastAPI
from dataset.router import router as dataset_router

app = FastAPI()
app.include_router(dataset_router, prefix="/datasets")