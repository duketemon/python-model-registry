from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

ModelVersionType = str
ModelExtensionType = str


@dataclass(kw_only=True, frozen=True)
class Model:
    """Machine Learning Model"""

    content: bytes
    name: str
    version: ModelVersionType
    file_extension: ModelExtensionType

    def to_dict(self) -> dict:
        """Exports a model to a dict

        :return: dictionary representation of the model
        """

        return asdict(self)

    def __str__(self) -> str:
        return ModelsRepository.create_model_file_name(
            self.name, self.version, self.file_extension
        )


class ModelsRepository(ABC):
    """Abstract Models Repository"""

    @abstractmethod
    def save_model(self, model: Model) -> None:
        """Saves the model to a storage

        :param model: ML model
        :raise ModelExistsError: when the model with specific version already exist
        """

    @abstractmethod
    def get_model(self, name: str, version: ModelVersionType) -> Model:
        """Returns an ML model

        :param name: name of the model
        :param version: version of the model
        :return: ML model
        :raise ModelNotFoundError: when the model with specific version doesn't exist
        """

    @abstractmethod
    def delete_model(self, name: str, version: ModelVersionType) -> None:
        """Deletes the model from a storage

        :param name: name of the model
        :param version: version of the model
        :raise ModelNotFoundError: when the model with specific version doesn't exist
        """

    @staticmethod
    def create_model_file_name(
        name: str, version: ModelVersionType, extension: ModelExtensionType
    ) -> str:
        """Creates the model file name

        :param name: name of the model
        :param version: version of the model
        :param extension: extension of the model file
        :return: file name of the model
        """

        file_name = f"{name}-{version}.{extension}"
        return file_name


class ModelExistsError(ValueError):
    """Raises when the model exists in a storage,
    and we're trying to save the very same model from the storage"""

    def __init__(self, name: str, version: ModelVersionType) -> None:
        filename = ModelsRepository.create_model_file_name(name, version, "")
        message = f"Model exists: {filename}"
        super().__init__(message)


class ModelNotFoundError(ValueError):
    """Raises when the model does not exist in a storage,
    and we're trying to fetch the very same model from the storage"""

    def __init__(self, name: str, version: ModelVersionType) -> None:
        filename = ModelsRepository.create_model_file_name(name, version, "")
        message = f"No such model: {filename}"
        super().__init__(message)
