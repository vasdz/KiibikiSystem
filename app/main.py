from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from fastapi.staticfiles import StaticFiles # <--- Импорт
from app.modules.ledger.router import router as ledger_router
from app.modules.posts.router import router as posts_router
from app.core.config import settings
from app.core.db import engine
from app.core.admin import setup_admin
from app.core.limiter import limiter
from app.modules.auth.router import router as auth_router
from app.modules.ledger.router import router as ledger_router
from app.modules.achievements.router import router as achievements_router
from app.modules.posts.router import router as posts_router
from app.core.middleware import SecurityHeadersMiddleware, ProcessTimeMiddleware
from app.core.logging import logger

# ТУТ НУЖНО ИМПОРТИРОВАТЬ ВСЕ МОДЕЛИ ДЛЯ АДМИНКИ И МИГРАЦИЙ
from app.modules.auth.models import User
from app.modules.ledger.models import Transaction
from app.modules.proofs.models import Proof
from app.modules.audit.models import AuditLog

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 System Starting... Security Protocols Active")
    yield
    logger.info("🛑 System Shutting Down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs"
)

# Подключаем лимитер к приложению
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

setup_admin(app, engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ProcessTimeMiddleware)

# --- РОУТЕРЫ ---
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(ledger_router, prefix=f"{settings.API_V1_STR}/ledger", tags=["Ledger"])
# Подключаем новый роутер достижений
app.include_router(achievements_router, prefix=f"{settings.API_V1_STR}", tags=["Achievements"]) # <--- [2] ДОБАВЛЕНО

app.include_router(posts_router, prefix=f"{settings.API_V1_STR}", tags=["Posts"])

app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.include_router(ledger_router, prefix=f"{settings.API_V1_STR}/ledger", tags=["Ledger"])
app.include_router(posts_router, prefix=f"{settings.API_V1_STR}/posts", tags=["Posts"])
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "ok", "system": "Kiibiki Secure Reward System"}
