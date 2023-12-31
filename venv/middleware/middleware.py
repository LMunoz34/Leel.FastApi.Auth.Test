from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def add_middleware(app: FastAPI):
    origins = [
        "http://localhost",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8000",
        "http://74.122.68.82",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
