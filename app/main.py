import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

from app.database import Base, engine, SessionLocal
from app.config import settings
from app.services.scheduler import init_scheduler, shutdown_scheduler, reload_pending_jobs


class SessionAuthMiddleware(BaseHTTPMiddleware):
    """Session-based auth — redirects to /login if not authenticated."""

    OPEN_PATHS = ("/login", "/penda/", "/static/")

    async def dispatch(self, request, call_next):
        path = request.url.path
        if any(path.startswith(p) for p in self.OPEN_PATHS):
            return await call_next(request)

        if request.session.get("authenticated"):
            return await call_next(request)

        return RedirectResponse(url="/login", status_code=303)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    init_scheduler()

    db = SessionLocal()
    try:
        reload_pending_jobs(db)
    finally:
        db.close()

    yield

    # Shutdown
    shutdown_scheduler()


app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionAuthMiddleware)
app.add_middleware(SessionMiddleware, secret_key="crm-session-secret-key")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routes
from app.routes.dashboard import router as dashboard_router
from app.routes.campaigns import router as campaigns_router
from app.routes.templates_routes import router as templates_router
from app.routes.replies import router as replies_router
from app.routes.admin import router as admin_router
from app.routes.penda import router as penda_router
from app.routes.auth import router as auth_router

app.include_router(dashboard_router)
app.include_router(campaigns_router)
app.include_router(templates_router)
app.include_router(replies_router)
app.include_router(admin_router)
app.include_router(penda_router)
app.include_router(auth_router)
