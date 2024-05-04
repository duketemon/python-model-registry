import pytest

from src.core.models_repositories.base import Model
from src.core.settings import MongoModelsRepositorySettings
from src.integrations.mongo.client import MongoClient
from tests.core.test_settings import models_repo_mongo_env_vars


@pytest.fixture()
def model() -> Model:
    return Model(
        name="my-model",
        version="0.0.7",
        content=b"binary repr of a model",
        file_extension="cbm",
    )


@pytest.fixture()
def mongo_client() -> MongoClient:
    args = {}
    for name, value in models_repo_mongo_env_vars.items():
        args[name.replace("models_repository__", "")] = value
    settings = MongoModelsRepositorySettings(**args)
    return MongoClient(settings)
