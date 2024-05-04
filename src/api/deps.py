from typing import Annotated

from fastapi import Depends

from src.core.models_repositories import (
    FileSystemModelsRepository,
    ModelsRepository,
    MongoModelsRepository,
)
from src.core.settings import Settings
from src.integrations.mongo.client import MongoClient


def create_settings() -> Settings:
    """Creates the instance of the app's settings"""

    return Settings()


def create_models_repository(
    settings: Annotated[Settings, Depends(create_settings)]
) -> ModelsRepository:
    """Creates an instance of the models repository

    :return: instance of the ModelsRepository
    :raise ValueError: when received unknown source
    """

    if settings.models_repository.source == "mongo":
        client = MongoClient(settings.models_repository)
        return MongoModelsRepository(client)

    if settings.models_repository.source == "fs":
        return FileSystemModelsRepository(settings.models_repository)

    raise ValueError(f"Received unknown source: {settings.models_repository.source}")
