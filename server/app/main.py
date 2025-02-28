from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import api

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://y.lol",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/api/v1")
