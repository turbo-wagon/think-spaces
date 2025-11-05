from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api import agents, artifacts, spaces
from .db import create_db_and_tables
from .storage import ensure_upload_dir
from . import web

# Load environment variables from .env file if present
load_dotenv()

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Ensure database tables exist on startup."""
    create_db_and_tables()
    ensure_upload_dir()
    yield


app = FastAPI(title="Think Spaces API", lifespan=lifespan)


@app.get("/health")
def read_health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def read_root() -> dict[str, str]:
    """Landing response for the API root."""
    return {
        "name": "Think Spaces API",
        "docs_url": "/docs",
        "ui_url": "/ui/spaces",
        "health_url": "/health",
    }


app.include_router(spaces.router)
app.include_router(artifacts.router)
app.include_router(agents.router)
app.include_router(web.router)

ensure_upload_dir()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
