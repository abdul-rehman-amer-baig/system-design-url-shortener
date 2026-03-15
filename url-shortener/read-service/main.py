from contextlib import asynccontextmanager

from fastapi import FastAPI

from routers import urls
from storage import close_db, init_db
from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="Read Service", lifespan=lifespan)

app.include_router(urls.router)


@app.get("/health")
async def health():
    return {"status": "ok", "instance": settings.INSTANCE_ID}