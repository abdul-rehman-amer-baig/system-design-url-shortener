from fastapi import FastAPI

from routers import users, urls

app = FastAPI(title="Write Service")

app.include_router(users.router)
app.include_router(urls.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "write-service"}
