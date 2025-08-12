from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncEngine

from .auth import router as auth_router, get_current_user
from .config import settings
from .db import engine
from .models import Base
from .routers.products import router as products_router
from .routers.licenses import router as licenses_router
from .routers.assignments import router as assignments_router
from .routers.purchase_orders import router as purchase_orders_router
from .routers.memos import router as memos_router


a_templates = Jinja2Templates(directory="app/templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup (simple dev convenience)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title=settings.site_name, lifespan=lifespan)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(licenses_router)
app.include_router(assignments_router)
app.include_router(purchase_orders_router)
app.include_router(memos_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return a_templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "site_name": settings.site_name,
        },
    )


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}