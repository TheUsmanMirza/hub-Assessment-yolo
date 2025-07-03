from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dataset.router import router as dataset_router

app = FastAPI(
    title="Dataset API",
    description="API for managing datasets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(dataset_router, prefix="/datasets")
