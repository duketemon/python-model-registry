import pytest

from src.core.models_repositories.base import ModelsRepository


@pytest.mark.parametrize(
    argnames="model_name, model_version, model_file_extension, expected_model_name",
    ids=("to use a file name", "to use as a file mask"),
    argvalues=(
        ("my-model", "1.2.3", "pickle", "my-model-1.2.3.pickle"),
        ("your-model", "4.0.4", "*", "your-model-4.0.4.*"),
    ),
)
def test_create_model_file_name(
    model_name, model_version, model_file_extension, expected_model_name
):
    # When
    actual_model_name = ModelsRepository.create_model_file_name(
        model_name, model_version, model_file_extension
    )

    # Then
    assert actual_model_name == expected_model_name
