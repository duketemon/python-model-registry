import pytest
from pymongo.database import Collection
from pytest import fixture

from src.core.models_repositories.mongo import (
    ModelExistsError,
    ModelNotFoundError,
    MongoModelsRepository,
)


@fixture()
def repo(mongo_client) -> MongoModelsRepository:
    repo = MongoModelsRepository(mongo_client)
    return repo


@fixture()
def collection_document() -> dict:
    return {"age": "55", "location": "Italy"}


@fixture()
def empty_collection_document() -> None:
    return None


def test_get_mongo_model_filter(model):
    # Given
    expected_filter = {"version": model.version}

    # When
    actual_filter = MongoModelsRepository.get_mongo_model_filter(model.version)

    # Then
    assert isinstance(actual_filter, dict)
    assert actual_filter == expected_filter


# is model exist
def test_is_model_exist_when_model_exists(mocker, repo, collection_document, model):
    # When
    mocker.patch.object(Collection, "find_one", return_value=collection_document)
    is_model_exist = repo.is_model_exist(model.name, model.version)

    # Then
    assert is_model_exist


def test_is_model_exist_when_model_not_found(mocker, repo, empty_collection_document, model):
    # When
    mocker.patch.object(Collection, "find_one", return_value=empty_collection_document)
    is_model_exist = repo.is_model_exist(model.name, model.version)

    # Then
    assert not is_model_exist


def test_save_model_when_model_exists_and_expects_model_exists_error(
    mocker, repo, model, collection_document
):
    # When
    mocker.patch.object(Collection, "find_one", return_value=collection_document)
    with pytest.raises(ModelExistsError):
        repo.save_model(model)


def test_save_model_when_model_does_not_exist_and_expects_no_problem(
    mocker, repo, model, empty_collection_document
):
    # When
    mocker.patch.object(Collection, "find_one", return_value=empty_collection_document)
    mocker.patch.object(Collection, "_insert_one", return_value="")
    repo.save_model(model)


def test_get_model_when_model_does_not_exist_and_expects_model_not_found_error(
    mocker, repo, model, empty_collection_document
):
    # When
    mocker.patch.object(Collection, "find_one", return_value=empty_collection_document)
    with pytest.raises(ModelNotFoundError):
        repo.get_model(model.name, model.version)


def test_get_model_when_model_exist_and_expects_no_problem(
    mocker, repo, model, collection_document
):
    # When
    mocker.patch.object(Collection, "find_one", return_value=model.to_dict())
    repo.get_model(model.name, model.version)


def test_delete_model_when_model_does_not_exist_and_expects_model_not_found_error(
    mocker, repo, model, empty_collection_document
):
    # When
    mocker.patch.object(Collection, "find_one", return_value=empty_collection_document)
    with pytest.raises(ModelNotFoundError):
        repo.delete_model(model.name, model.version)


def test_delete_model_when_model_exist_and_expects_no_problem(
    mocker, repo, model, collection_document
):
    # When
    mocker.patch.object(Collection, "find_one", return_value=model.to_dict())
    mocker.patch.object(Collection, "_delete_retryable", return_value={"n": 1})
    repo.delete_model(model.name, model.version)
