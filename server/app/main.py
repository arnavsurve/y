from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import api

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://y.lol",
        f"http://localhost:{settings.app_port}",
        f"http://127.0.0.1:{settings.app_port}",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/api/v1")
