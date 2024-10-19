import logging

import uvicorn
from fastapi import FastAPI
from omegaconf import OmegaConf
from app.api.routes import data, eligibility, items, model, users
from app.db.database import create_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_path: str = "src/app/conf/config.yaml") -> FastAPI:
    """
    Create a FastAPI application with the specified configuration.
    Args:
        config_path: The path to the configuration file in yaml format

    Returns:
        FastAPI: The FastAPI application instance.
    """
    config = OmegaConf.load(config_path)

    api_router = FastAPI(title=config.api.title, description=config.api.description, version=config.api.version)

    api_router.include_router(users.router, prefix="/users", tags=["users"])
    api_router.include_router(items.router, prefix="/items", tags=["items"])
    api_router.include_router(model.router, prefix="/model", tags=["model"])
    api_router.include_router(eligibility.router, prefix="/eligibility", tags=["eligibility"])
    api_router.include_router(data.router, prefix="/data", tags=["data"])

    return api_router


if __name__ == "__main__":
    config_path = "./backend/src/app/conf/config.yaml"
    config = OmegaConf.load(config_path)
    create_tables()
    app = create_app(config_path)
    logger.info("Starting the API server...")
    uvicorn.run(app, host=config.api.host, port=config.api.port, log_level="info")
    logger.info("API server stopped.")
