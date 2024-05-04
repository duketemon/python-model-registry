import dataclasses
import re
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from src.api.run import app, create_models_repository
from src.core.models_repositories import FileSystemModelsRepository, Model
from src.core.settings import FileSystemModelsRepositorySettings


@pytest.fixture()
def client(tmp_path) -> TestClient:
    settings = FileSystemModelsRepositorySettings(source="fs", directory=str(tmp_path))
    app.dependency_overrides[create_models_repository] = lambda: FileSystemModelsRepository(
        settings
    )
    return TestClient(app)


def create_crud_params(model):
    return {"name": model.name, "version": model.version}


def create_files(model: Model) -> dict:
    return {"file": (str(model), BytesIO(model.content))}


def test_health_check(client):
    # Given
    url = "/health_check"

    # When
    response = client.get(url)

    # Then
    assert response.status_code == 200
    assert "alive" in response.text


# save model
def test_save_model_when_model_is_not_in_storage(client, model):
    # Given
    model_as_file = create_files(model)
    params = create_crud_params(model)

    # save the model
    response = client.post("/", params=params, files=model_as_file)
    assert response.status_code == 200

    # fetch the model to verify
    response = client.get("/", params=params)
    assert response.status_code == 200
    assert response.content == model.content


def test_save_model_when_storage_contains_model_with_such_name_and_version_saved_and_expects_model_exists_error(
    client, model
):
    # Given
    model_as_file = create_files(model)
    params = create_crud_params(model)

    # save the model
    response = client.post("/", params=params, files=model_as_file)
    assert response.status_code == 200

    # save the model
    response = client.post("/", params=params, files=model_as_file)
    assert response.status_code == 409
    assert "model exists" in response.text.lower()


def test_save_model_when_model_filename_does_not_have_any_file_extension_and_expects_mlmodel_as_a_file_extension(
    client, model
):
    # Given
    params = create_crud_params(model)
    model_as_file = create_files(model)
    name, file = model_as_file["file"]
    model_as_file["file"] = "model2", file
    expected_file_name = "my-model-0.0.7.mlmodel"

    # save the model
    response = client.post("/", params=params, files=model_as_file)
    assert response.status_code == 200

    # fetch the model to verify
    response = client.get("/", params=params)
    assert response.status_code == 200
    content_disposition = response.headers["content-disposition"]
    actual_filename = re.findall("filename=(.+)", content_disposition)[0]
    assert actual_filename == expected_file_name


# get model
def test_get_model_when_model_is_not_found_and_expects_not_found_item_error_returned(
    client, model
):
    # Given
    params = create_crud_params(model)

    # fetch the model
    response = client.get("/", params=params)
    assert response.status_code == 404
    assert "no such model" in response.text.lower()


def test_get_model_when_model_is_in_storage_and_expects_model_file_as_a_response(client, model):
    # Given
    model_as_file = create_files(model)
    params = create_crud_params(model)
    # save the model to the storage
    response = client.post("/", params=params, files=model_as_file)
    assert response.status_code == 200

    # fetch the model
    response = client.get("/", params=params)
    assert response.status_code == 200
    assert response.content == model.content


def test_get_model_when_model_is_in_storage_and_get_model_request_sent_several_times(
    client, model
):
    # Given
    model_as_file = create_files(model)
    params = create_crud_params(model)
    # save the model to the storage
    response = client.post("/", params=params, files=model_as_file)
    assert response.status_code == 200

    for _ in range(3):
        # fetch the model
        response = client.get("/", params=params)
        assert response.status_code == 200
        assert response.content == model.content


# delete model
def test_delete_model_when_model_is_not_exist_in_storage_and_expects_item_not_found_error_returned(
    client, model
):
    # Given
    params = create_crud_params(model)

    # check that the model is not in the storage
    # expects 404 error
    response = client.get("/", params=params)
    assert response.status_code == 404

    # delete model from the storage
    # expects 404 error because there's no such model
    response = client.delete("/", params=params)
    assert response.status_code == 404


def test_delete_model_when_model_exists_in_storage_and_has_been_deleted_twice(client, model):
    # Given
    model_as_file = create_files(model)
    params = create_crud_params(model)

    # check that the model is not in the storage
    # expects 404 error
    response = client.get("/", params=params)
    assert response.status_code == 404

    # save the model to the storage
    response = client.post("/", params=params, files=model_as_file)
    assert response.status_code == 200

    # delete the model from the storage
    response = client.delete("/", params=params)
    assert response.status_code == 200

    # delete the model from the storage
    # expects 404 error because there's no such model anymore
    response = client.delete("/", params=params)
    assert response.status_code == 404


def test_delete_model_when_model_is_in_storage_and_has_been_deleted_once(client, model):
    # Given
    model_as_file = create_files(model)
    params = create_crud_params(model)

    # check that the model is not in the storage
    # expects 404 error
    response = client.get("/", params=params)
    assert response.status_code == 404

    # save the model to the storage
    response = client.post("/", params=params, files=model_as_file)
    assert response.status_code == 200

    # get the model from the storage
    # to confirm the model saved correctly
    response = client.get("/", params=params)
    assert response.status_code == 200
    assert response.content == model.content

    # delete model from the storage
    response = client.delete("/", params=params)
    assert response.status_code == 200

    # check the model is not in the storage anymore
    # expects 404 error
    response = client.get("/", params=params)
    assert response.status_code == 404


# different scenarios
def test_case_when_storage_contains_models_with_the_same_name_but_different_versions_and_no_collisions_expects(
    client, model
):
    # Given
    model_as_file = create_files(model)
    model_params = create_crud_params(model)

    another_model = dataclasses.replace(
        model, content=b"different content of a model", version="i.o.x"
    )
    assert another_model != model.content
    another_model_as_file = create_files(another_model)
    another_model_params = create_crud_params(another_model)

    # save one model
    response = client.post("/", params=model_params, files=model_as_file)
    assert response.status_code == 200

    # save another model
    response = client.post("/", params=another_model_params, files=another_model_as_file)
    assert response.status_code == 200

    # fetch the model to verify
    response = client.get("/", params=model_params)
    assert response.status_code == 200
    assert response.content == model.content

    # fetch another model to verify
    response = client.get("/", params=another_model_params)
    assert response.status_code == 200
    assert response.content == another_model.content

    assert another_model != model.content


def test_case_when_several_storage_contains_models_with_the_same_version_but_different_names_and_no_collisions_expects(
    client, model
):
    # Given
    model_as_file = create_files(model)
    model_params = create_crud_params(model)

    another_model = dataclasses.replace(
        model, content=b"different content of a model", name="your-model-2"
    )
    assert another_model != model.content
    another_model_as_file = create_files(another_model)
    another_model_params = create_crud_params(another_model)

    # save one model
    response = client.post("/", params=model_params, files=model_as_file)
    assert response.status_code == 200

    # save another model
    response = client.post("/", params=another_model_params, files=another_model_as_file)
    assert response.status_code == 200

    # fetch the model to verify
    response = client.get("/", params=model_params)
    assert response.status_code == 200
    assert response.content == model.content

    # fetch another model to verify
    response = client.get("/", params=another_model_params)
    assert response.status_code == 200
    assert response.content == another_model.content

    # models are different and not point to the same space in memory
    assert another_model != model.content
