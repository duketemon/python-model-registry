from pathlib import Path
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, PositiveInt
from pydantic_settings import BaseSettings


class FileSystemModelsRepositorySettings(BaseModel):
    """Settings of the local file models repository"""

    source: Literal["fs"]
    directory: str


class MongoModelsRepositorySettings(BaseModel):
    """Settings of the Mongo DB models repository"""

    source: Literal["mongo"]
    host: str
    port: PositiveInt
    username: str
    password: str
    database_name: str

    @property
    def connection(self):
        """Mongo DB connection string"""

        return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}"


ModelsRepository = Annotated[
    Union[
        FileSystemModelsRepositorySettings,
        MongoModelsRepositorySettings,
    ],
    Field(discriminator="source"),
]


class Settings(BaseSettings):
    """Settings of the app"""

    def __init__(self, env_file: str | Path | None = None, **kwargs) -> None:
        super().__init__(_env_file=env_file, _env_nested_delimiter="__", **kwargs)

    version: str
    environment: str
    models_repository: ModelsRepository
