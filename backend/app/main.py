import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.core.logging import setup_logging
from app.core.security import setup_security
from app.core.errors import AppError, app_error_handler
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.status import router as status_router
from app.api.documents import router as documents_router
from app.api.compare import router as compare_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


app = FastAPI(
    title="ClauseCompass API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers
setup_security(app)

# Error Handlers
app.add_exception_handler(AppError, app_error_handler)

# Routers
app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(status_router)
app.include_router(documents_router)
app.include_router(compare_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
