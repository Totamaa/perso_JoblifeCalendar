from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from config.settings import get_settings
from config.logs import LoggerManager
from api.router import api_router

def create_app() -> FastAPI:
    
    settings = get_settings()
    logging = LoggerManager()
    
    docs_url = None
    redoc_url = None
    if settings.ENVIRONMENT != "prod":
        docs_url = "/docs"
        redoc_url = "/redoc"
        
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logging.info("Start lifespan")
        yield
        logging.info("Stop lifespan")
    
    app = FastAPI(
        title=settings.BACK_NAME,
        description=settings.BACK_DESCRIPTION,
        version=settings.BACK_VERSION,
        docs_url=docs_url,
        redoc_url=redoc_url,
        lifespan=lifespan
    )
    
    app.include_router(api_router, prefix="/api")
    
    logging.info("Start backend")
    
    return app

app = create_app()