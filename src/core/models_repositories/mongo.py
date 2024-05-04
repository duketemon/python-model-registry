from src.integrations.mongo.client import MongoClient

from .base import (
    Model,
    ModelExistsError,
    ModelNotFoundError,
    ModelsRepository,
    ModelVersionType,
)


class MongoModelsRepository(ModelsRepository):
    """Mongo DB implementation of the models repository"""

    def __init__(self, client: MongoClient) -> None:
        self.client = client

    def save_model(self, model: Model) -> None:
        if self.is_model_exist(model.name, model.version):
            raise ModelExistsError(model.name, model.version)

        data = model.to_dict()
        self.client.save_one_item(model.name, data)

    def get_model(self, name: str, version: ModelVersionType) -> Model:
        if not self.is_model_exist(name, version):
            raise ModelNotFoundError(name, version)

        filter_ = self.get_mongo_model_filter(version)
        data = self.client.get_one_item(name, filter_)
        if data is None:
            raise ModelNotFoundError(name, version)
        if "_id" in data:
            del data["_id"]

        model = Model(**data)
        return model

    def delete_model(self, name: str, version: ModelVersionType) -> None:
        if not self.is_model_exist(name, version):
            raise ModelNotFoundError(name, version)

        self.client.delete_one_item(name, self.get_mongo_model_filter(version))

    def is_model_exist(self, name: str, version: ModelVersionType) -> bool:
        """Check if model exist in the storage"""

        document = self.client.get_one_item(name, self.get_mongo_model_filter(version))
        return document is not None

    @staticmethod
    def get_mongo_model_filter(version: ModelVersionType) -> dict:
        """Generates a filter that will be used for CRUD operations"""

        return {"version": version}
