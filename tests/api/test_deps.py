import pytest
from pydantic import ValidationError

from src.api.deps import ModelsRepository, create_models_repository, create_settings
from src.core.models_repositories import (
    FileSystemModelsRepository,
    MongoModelsRepository,
)
from src.core.settings import (
    FileSystemModelsRepositorySettings,
    MongoModelsRepositorySettings,
    Settings,
)
from tests.core.test_settings import (
    fs_is_models_repo_env_vars_sample,
    given_env_vars_via_shell_variables,
    mongo_is_models_repo_env_vars_sample,
)


def test_create_settings_when_no_environment_variables_have_not_being_prepared_for_the_run_and_expects_validation_error():
    with pytest.raises(ValidationError):
        create_settings()


@given_env_vars_via_shell_variables(fs_is_models_repo_env_vars_sample)
def test_create_models_repository_when_source_is_file_system_and_expects_an_instance_of_file_system_models_repository_settings():
    # Given
    settings = create_settings()

    # When
    models_repository = create_models_repository(settings)

    # Then
    assert isinstance(models_repository, ModelsRepository)
    assert isinstance(models_repository, FileSystemModelsRepository)
    assert isinstance(settings.models_repository, FileSystemModelsRepositorySettings)


@given_env_vars_via_shell_variables(mongo_is_models_repo_env_vars_sample)
def test_create_models_repository_when_source_is_mongo_db_and_expects_an_instance_of_mongo_system_models_repository_settings():
    # Given
    settings = create_settings()

    # When
    models_repository = create_models_repository(settings)

    # Then
    assert isinstance(models_repository, ModelsRepository)
    assert isinstance(models_repository, MongoModelsRepository)
    assert isinstance(settings.models_repository, MongoModelsRepositorySettings)
