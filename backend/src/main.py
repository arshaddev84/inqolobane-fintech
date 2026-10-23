"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from config.settings import get_settings

settings = get_settings()
app = FastAPI(title="Inqolobane Operations API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(
        dict.fromkeys(
            [*settings.cors_origins, "http://localhost:3000", "http://127.0.0.1:3000"]
        )
    ),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)
app.include_router(api_router)