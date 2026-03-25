# config.py
import os
from datetime import timedelta
from decimal import Decimal


class Config:
    # --- CAMINHOS E DIRETÓRIOS (persistência segura) ---
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    UPLOAD_BASE_PATH = os.environ.get("UPLOAD_PATH") or os.path.join(
        BASE_DIR, "data_storage"
    )
    UPLOAD_FOLDER_PUBLIC = os.path.join(UPLOAD_BASE_PATH, "public")
    UPLOAD_FOLDER_PRIVATE = os.path.join(UPLOAD_BASE_PATH, "private")

    # --- SEGURANÇA (obrigatória) ---
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY and os.environ.get("FLASK_ENV") in ["production", "prod"]:
        raise ValueError("SECRET_KEY é OBRIGATÓRIO em produção!")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = 3600

    # --- SESSÕES E COOKIES (UX Angola + segurança) ---
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PREFERRED_URL_SCHEME = "https"

    # --- RATE LIMITING (anti-DoS para Next.js) ---
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_HEADERS_ENABLED = False

    # --- NEGÓCIO (Single Source of Truth) ---
    AGROKONGO_TAXA = Decimal("0.05")  # ← Decimal para precisão financeira
    ITEMS_PER_PAGE = 12
    TIMEZONE = "Africa/Luanda"

    # --- CDN (Cloudflare R2 / AWS S3) ---
    CDN_ENABLED = os.environ.get("CDN_ENABLED", "False").lower() == "true"
    CDN_URL = os.environ.get("CDN_URL", "")
    CDN_BUCKET = os.environ.get("CDN_BUCKET", "agrokongo-safras")
    CDN_AWS_ACCESS_KEY = os.environ.get("CDN_AWS_ACCESS_KEY")
    CDN_AWS_SECRET_KEY = os.environ.get("CDN_AWS_SECRET_KEY")
    CDN_AWS_REGION = os.environ.get("CDN_AWS_REGION", "us-east-1")

    # --- Configurações para Next.js + JWT ---
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or os.environ.get("SECRET_KEY")
    CORS_ORIGINS = ["http://localhost:3000", "https://agrokongo.ao"]


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEV_DATABASE_URL")
        or f"sqlite:///{os.path.join(Config.BASE_DIR, 'agrokongo_dev.db')}"
    )

    # Dev: cookies sem HTTPS + Redis em memória
    SESSION_COOKIE_SECURE = False
    RATELIMIT_STORAGE_URL = "memory://"


class ProductionConfig(Config):
    DEBUG = False

    # Banco PostgreSQL obrigatório
    uri = os.environ.get("DATABASE_URL")
    if not uri:
        raise ValueError("DATABASE_URL é OBRIGATÓRIO em produção!")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+psycopg2://", 1)
    SQLALCHEMY_DATABASE_URI = uri

    # Segurança reforçada
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Pool de conexões otimizado
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.environ.get("DB_POOL_SIZE", 15)),
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", 25)),
        "pool_recycle": 1800,
        "pool_pre_ping": True,
        "pool_timeout": 15,
    }

    @classmethod
    def init_app(cls, app):
        # Verificações críticas de produção
        if not cls.SECRET_KEY or len(cls.SECRET_KEY) < 40:
            raise ValueError("SECRET_KEY fraco ou ausente em produção!")
        if not app.config.get("REDIS_URL"):
            raise ValueError("REDIS_URL é OBRIGATÓRIO em produção (Limiter + Celery)!")
        if not os.environ.get("AFRICAS_TALKING_API_KEY"):
            app.logger.warning(
                "AFRICAS_TALKING_API_KEY não configurado (OTP desativado)"
            )


# ==================== CONFIG DICT ====================
config_dict = {
    "dev": DevelopmentConfig,
    "development": DevelopmentConfig,
    "prod": ProductionConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
