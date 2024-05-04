from pymongo import MongoClient as _MongoClient

from src.core.settings import MongoModelsRepositorySettings


class MongoClient:
    """Mongo DB client"""

    def __init__(self, settings: MongoModelsRepositorySettings) -> None:
        client: _MongoClient = _MongoClient(settings.connection)
        self.database = client[settings.database_name]

    def save_one_item(self, collection_name: str, document: dict) -> str:
        """Saves one item to the collection

        :param collection_name: collection name
        :param document: document
        :return: id of the saved document
        """

        collection = self.database[collection_name]
        response = collection.insert_one(document)
        return response.inserted_id

    def get_one_item(self, collection_name: str, collection_filter: dict) -> dict | None:
        """Fetches one item from the collection

        :param collection_name: collection name
        :param collection_filter: collection filter
        :return: document or None if there's no documents satisfied to the `collection_filter`
        """

        collection = self.database[collection_name]
        document = collection.find_one(collection_filter)
        return document

    def delete_one_item(self, collection_name: str, collection_filter: dict) -> int:
        """Deletes one item from the collection

        :param collection_name: collection name
        :param collection_filter: filter to be used to delete an item
        :return: number of deleted items
        """

        collection = self.database[collection_name]
        response = collection.delete_one(collection_filter)
        return response.deleted_count
