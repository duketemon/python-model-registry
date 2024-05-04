from io import BytesIO

import pytest
import requests

from src.core.models_repositories import Model


def create_crud_params(model):
    return {"name": model.name, "version": model.version}


def create_files(model: Model) -> dict:
    return {"file": (str(model), BytesIO(model.content))}


@pytest.fixture
def base_url() -> str:
    return "http://localhost:8000"


@pytest.fixture()
def model() -> Model:
    return Model(
        name="my-model",
        version="0.0.7",
        content=b"binary repr of a model",
        file_extension="cbm",
    )


def test_health_check(base_url):
    # Given
    url = base_url + "/health_check"

    # When
    response = requests.get(url)

    # Then
    assert response.status_code == 200
    assert "alive" in response.text


def test_save_new_model_successfully(base_url, model):
    # Given
    model_as_file = create_files(model)
    params = create_crud_params(model)
    url = base_url + "/"

    # save the model
    response = requests.post(url, params=params, files=model_as_file)
    assert response.status_code == 200

    # fetch the model to verify
    response = requests.get(url, params=params)
    assert response.status_code == 200
    assert response.content == model.content

    # fetch the model to verify
    response = requests.get(url, params=params)
    assert response.status_code == 200
    assert response.content == model.content

    # delete the saved model to clean up
    response = requests.delete(url, params=params)
    assert response.status_code == 200


def test_save_model_with_existing_name_and_version(base_url, model):
    # Given
    model_as_file = create_files(model)
    params = create_crud_params(model)
    url = base_url + "/"
    # save the model
    response = requests.post(url, params=params, files=model_as_file)
    assert response.status_code == 200

    # save the model
    response = requests.post(url, params=params, files=model_as_file)
    assert response.status_code == 409
    assert "model exists" in response.text.lower()

    # delete the saved model to clean up
    response = requests.delete(url, params=params)
    assert response.status_code == 200


def test_fetch_existing_model_successfully(base_url, model):
    # Given
    model_as_file = create_files(model)
    params = create_crud_params(model)
    url = base_url + "/"
    # save the model to the storage
    response = requests.post(url, params=params, files=model_as_file)
    assert response.status_code == 200

    # fetch the model
    response = requests.get(base_url, params=params)
    assert response.status_code == 200
    assert response.content == model.content

    # delete the saved model to clean up
    response = requests.delete(url, params=params)
    assert response.status_code == 200


def test_fetch_non_existent_model(base_url, model):
    # Given
    params = create_crud_params(model)
    url = base_url + "/"

    # fetch the model
    response = requests.get(url, params=params)
    assert response.status_code == 404
    assert "no such model" in response.text.lower()


def test_delete_existing_model_successfully(base_url, model):
    # Given
    model_as_file = create_files(model)
    params = create_crud_params(model)
    url = base_url + "/"
    # save the model to the storage
    response = requests.post(url, params=params, files=model_as_file)
    assert response.status_code == 200

    # delete model from the storage
    response = requests.delete(url, params=params)
    assert response.status_code == 200

    # check the model is not in the storage anymore
    # expects 404 error
    response = requests.get(url, params=params)
    assert response.status_code == 404


def test_delete_non_existent_model(base_url, model):
    # Given
    params = create_crud_params(model)
    url = base_url + "/"

    # delete model from the storage
    # expects 404 error because there's no such model
    response = requests.delete(url, params=params)
    assert response.status_code == 404
    assert "no such model" in response.text.lower()
