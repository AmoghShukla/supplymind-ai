from contextlib import asynccontextmanager
from fastapi import FastAPI
from .api.routes import router
from .core.config import settings
from .db import engine
from .models import Base
from .seed import seed
@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection: await connection.run_sync(Base.metadata.create_all)
    if settings.auto_seed: await seed()
    yield
app = FastAPI(title="SupplyMind AI", version="1.0.0", lifespan=lifespan)
app.include_router(router)
@app.get("/health")
async def health(): return {"status": "ok", "provider": settings.ai_provider}
