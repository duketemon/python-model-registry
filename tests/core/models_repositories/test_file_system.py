import dataclasses
import os
from pathlib import Path

import pytest

from src.core.models_repositories.file_system import (
    CompromisedFileStructureError,
    FileSystemModelsRepository,
    ModelExistsError,
    ModelNotFoundError,
    save_binary_data_to_file,
)
from src.core.settings import FileSystemModelsRepositorySettings


class FakeModelContextManager:
    def __init__(self, file_path: str | Path, data: bytes):
        self.file_path = file_path
        self.data = data

    def __enter__(self):
        save_binary_data_to_file(self.file_path, self.data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.file_path)


@pytest.fixture()
def repo(tmp_path):
    settings = FileSystemModelsRepositorySettings(source="fs", directory=str(tmp_path))
    return FileSystemModelsRepository(settings)


def test_create_model_path(repo, model):
    # When
    path = str(repo.create_model_path(model))

    # Then
    assert str(repo.resources_dir) in path
    assert model.name in path
    assert model.version in path
    assert path.endswith(model.file_extension)


# find model path
def test_find_model_path_when_file_structure_was_ruined_and_expects_compromised_file_structure_error(
    repo, model
):
    # Given
    dup_model = dataclasses.replace(model, file_extension=".cbmext")
    dup_model_path = repo.create_model_path(dup_model)
    model_path = repo.create_model_path(model)

    # When
    with FakeModelContextManager(dup_model_path, dup_model.content):
        with FakeModelContextManager(model_path, model.content):
            assert os.path.exists(dup_model_path)
            assert os.path.exists(model_path)
            with pytest.raises(CompromisedFileStructureError):
                repo.find_model_path(model.name, model.version)


def test_find_model_path_when_no_file_found_and_expects_none_values(repo, model):
    # When
    actual_model_path = repo.find_model_path(model.name, model.version)

    # Then
    assert actual_model_path is None


def test_find_model_path_when_only_one_file_found_and_expects_path_to_it(repo, model):
    # Given
    model_path = repo.create_model_path(model)

    # When
    with FakeModelContextManager(model_path, model.content):
        actual_model_path = repo.find_model_path(model.name, model.version)

        assert os.path.exists(actual_model_path)

    path = str(actual_model_path)

    # Then
    assert str(repo.resources_dir) in path
    assert model.name in path
    assert model.version in path
    assert path.endswith(model.file_extension)


# delete model
def test_delete_model_when_model_does_not_exist_and_expects_raise_model_not_found_error(
    repo, model
):
    # Then
    with pytest.raises(ModelNotFoundError):
        # When
        repo.delete_model(model.name, model.version)


def test_delete_model_when_only_one_model_exist(repo, model):
    # Given
    model_path = repo.create_model_path(model)
    save_binary_data_to_file(model_path, model.content)
    assert os.path.exists(model_path)

    # When
    repo.delete_model(model.name, model.version)

    # Then
    assert not os.path.exists(model_path)


def test_delete_model_when_model_versions_match_but_names_are_different(repo, model):
    """my-model of 1.0 version and your-model of 1.0 version are different models"""

    # Given
    dup_model = dataclasses.replace(model, name="your-model")
    dup_model_path = repo.create_model_path(dup_model)
    model_path = repo.create_model_path(model)

    with FakeModelContextManager(dup_model_path, dup_model.content):
        save_binary_data_to_file(model_path, model.content)
        assert os.path.exists(model_path)
        assert os.path.exists(dup_model_path)
        repo.delete_model(model.name, model.version)
        assert not os.path.exists(model_path)
        assert os.path.exists(dup_model_path)


def test_delete_model_when_model_names_match_but_versions_are_different(repo, model):
    """my-model of 1.0 version and my-model of 4.0 version are different models"""

    # Given
    dup_model = dataclasses.replace(model, version="i.o.x")
    dup_model_path = repo.create_model_path(dup_model)
    model_path = repo.create_model_path(model)

    with FakeModelContextManager(dup_model_path, dup_model.content):
        save_binary_data_to_file(model_path, model.content)
        assert os.path.exists(model_path)
        assert os.path.exists(dup_model_path)
        repo.delete_model(model.name, model.version)
        assert not os.path.exists(model_path)
        assert os.path.exists(dup_model_path)


# get model
def test_get_model_when_model_does_not_exist_and_expects_raise_model_not_found_error(repo, model):
    # Then
    with pytest.raises(ModelNotFoundError):
        # When
        repo.get_model(model.name, model.version)


def test_get_model_when_only_one_model_exists(repo, model):
    # Given
    model_path = repo.create_model_path(model)

    with FakeModelContextManager(model_path, model.content):
        # When
        fetched_model = repo.get_model(model.name, model.version)

    # Then
    assert fetched_model == model


def test_get_model_when_model_versions_match_but_names_are_different(repo, model):
    """my-model of 1.0 version and your-model of 1.0 version are different models"""

    # Given
    dup_model = dataclasses.replace(model, name="your-model")
    dup_model_path = repo.create_model_path(dup_model)
    model_path = repo.create_model_path(model)

    with FakeModelContextManager(dup_model_path, dup_model.content):
        with FakeModelContextManager(model_path, model.content):
            assert os.path.exists(model_path)
            assert os.path.exists(dup_model_path)
            actual_model = repo.get_model(model.name, model.version)

    assert actual_model == model


def test_get_model_when_model_names_match_but_versions_are_different(repo, model):
    """my-model of 1.0 version and my-model of 4.0 version are different models"""

    # Given
    dup_model = dataclasses.replace(model, version="i.o.x")
    dup_model_path = repo.create_model_path(dup_model)
    model_path = repo.create_model_path(model)

    with FakeModelContextManager(dup_model_path, dup_model.content):
        with FakeModelContextManager(model_path, model.content):
            assert os.path.exists(model_path)
            assert os.path.exists(dup_model_path)
            actual_model = repo.get_model(model.name, model.version)

    assert actual_model == model


# save model
def test_save_model_when_model_does_not_exist(repo, model):
    # Given
    model_path = repo.create_model_path(model)

    # When
    repo.save_model(model)

    # Then
    assert os.path.exists(model_path)


def test_save_model_when_model_exists_and_expects_raise_model_exists_error(repo, model):
    # Given
    model_path = repo.create_model_path(model)

    with FakeModelContextManager(model_path, model.content):
        with pytest.raises(ModelExistsError):
            repo.save_model(model)


def test_save_model_when_model_versions_match_but_names_are_different(repo, model):
    """my-model of 1.0 version and your-model of 1.0 version are different models"""

    # Given
    given_model = dataclasses.replace(model, name="your-model")
    model_path = repo.create_model_path(model)

    with FakeModelContextManager(model_path, model.content):
        assert os.path.exists(model_path)
        repo.save_model(given_model)

    model_path_of_given_model = repo.create_model_path(given_model)
    assert os.path.exists(model_path_of_given_model)


def test_save_model_when_model_names_match_but_versions_are_different(repo, model):
    """my-model of 1.0 version and my-model of 4.0 version are different models"""

    # Given
    given_model = dataclasses.replace(model, version="i.o.x")
    model_path = repo.create_model_path(model)

    with FakeModelContextManager(model_path, model.content):
        assert os.path.exists(model_path)
        repo.save_model(given_model)

    model_path_of_given_model = repo.create_model_path(given_model)
    assert os.path.exists(model_path_of_given_model)
