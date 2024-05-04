import os
import re
from pathlib import Path

from src.core.settings import FileSystemModelsRepositorySettings

from .base import (
    Model,
    ModelExistsError,
    ModelNotFoundError,
    ModelsRepository,
    ModelVersionType,
)


class FileSystemModelsRepository(ModelsRepository):
    """Models repository that uses file system to save models"""

    def __init__(self, settings: FileSystemModelsRepositorySettings) -> None:
        self.resources_dir = settings.directory
        # if not os.path.exists(self.resources_dir):
        #     os.mkdir(self.resources_dir)

    def save_model(self, model: Model) -> None:
        model_path = self.find_model_path(model.name, model.version)
        if model_path is not None:
            raise ModelExistsError(model.name, model.version)

        model_path = self.create_model_path(model)
        save_binary_data_to_file(model_path, model.content)

    def get_model(self, name: str, version) -> Model:
        model_path = self.find_model_path(name, version)
        if model_path is None:
            raise ModelNotFoundError(name, version)

        content = read_binary_data_from_file(model_path)
        extension = model_path.suffix[1:]
        model = Model(content=content, name=name, version=version, file_extension=extension)
        return model

    def delete_model(self, name: str, version: ModelVersionType) -> None:
        model_path = self.find_model_path(name, version)
        if model_path is None:
            raise ModelNotFoundError(name, version)

        os.remove(model_path)

    def create_model_path(self, model: Model) -> Path:
        """Creates full path to the model

        :param model: ML model
        :return: full path to the provided model
        """

        file_name = self.create_model_file_name(model.name, model.version, model.file_extension)
        model_path = Path(self.resources_dir, file_name)
        return model_path

    def find_model_path(self, model_name: str, model_version: ModelVersionType) -> Path | None:
        """Finding for the model file by its name and version

        :param model_name: model name
        :param model_version: model version
        :return: path to the model binaries if it exists otherwise None
        :raise CompromisedFileStructureError
        """
        model_pattern = self.create_model_file_name(model_name, model_version, ".*")
        files = [f for f in os.listdir(self.resources_dir) if re.match(model_pattern, f)]

        if len(files) > 1:
            raise CompromisedFileStructureError(model_pattern, self.resources_dir)

        if files:
            path = Path(os.path.join(self.resources_dir, files[0])).absolute()
            return path
        return None


class CompromisedFileStructureError(ValueError):
    """Raises when the file structure of the directory has been changed"""

    def __init__(self, model_pattern: str, directory: str | Path) -> None:
        message = (
            f"File structure of the directory {directory} has been ruined. "
            f"There are several files satisfied to the following pattern '{model_pattern}'"
        )
        super().__init__(message)


def save_binary_data_to_file(file_path: str | Path, binary_data: bytes) -> None:
    """Saves binary data to the file

    :param file_path: file path
    :param binary_data: binary data to be saved
    """

    with open(file_path, "wb") as file:
        file.write(binary_data)


def read_binary_data_from_file(file_path: str | Path) -> bytes:
    """Reads binary data from the file

    :param file_path: file path
    :return: binary data
    """

    with open(file_path, "rb") as file:
        return file.read()
