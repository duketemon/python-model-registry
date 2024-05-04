import os
from typing import Final

import pytest
from pydantic import ValidationError

from src.core.settings import Settings

common_env_vars: Final[dict[str, str]] = {"version": "4.0.4", "environment": "test"}

models_repo_fs_env_vars: Final[dict[str, str]] = {
    "models_repository__source": "fs",
    "models_repository__directory": "resources",
}

models_repo_mongo_env_vars: Final[dict[str, str]] = {
    "models_repository__source": "mongo",
    "models_repository__host": "localhost",
    "models_repository__port": "12345",
    "models_repository__username": "testusername",
    "models_repository__password": "testpassword",
    "models_repository__database_name": "model-registry",
}


fs_is_models_repo_env_vars_sample = dict(**common_env_vars, **models_repo_fs_env_vars)
mongo_is_models_repo_env_vars_sample = dict(**common_env_vars, **models_repo_mongo_env_vars)


def given_env_vars_via_shell_variables(*env_sets):
    def decorator(function):
        def wrapper(*args, **kwargs):
            env_vars = {}
            for envs in env_sets:
                env_vars.update(**envs)
            os.environ.update(env_vars)

            function(*args, **kwargs)

            for name in env_vars:
                del os.environ[name]

        return wrapper

    return decorator


def given_env_vars_via_dot_env_file(*env_sets):
    def decorator(function):
        def wrapper():
            env_vars = dict()
            for envs in env_sets:
                env_vars.update(**envs)

            env_path = "_test_.env"
            with open(env_path, "w") as file:
                content = "\n".join(f"{name}={value}" for name, value in env_vars.items())
                file.write(content)

            function(env_path)

            # delete the file
            os.remove(env_path)

        return wrapper

    return decorator


# Mongo DB
@given_env_vars_via_dot_env_file(mongo_is_models_repo_env_vars_sample)
def test_settings_when_source_is_mongodb_and_variables_set_up_via_dot_env_file(env_path):
    # When
    settings = Settings(env_file=env_path)

    # Then
    assert settings.version == "4.0.4"
    assert settings.environment == "test"
    assert settings.models_repository.database_name == "model-registry"
    assert settings.models_repository.source == "mongo"
    assert settings.models_repository.host == "localhost"
    assert settings.models_repository.port == 12345
    assert settings.models_repository.username == "testusername"
    assert settings.models_repository.password == "testpassword"
    assert (
        settings.models_repository.connection
        == "mongodb://testusername:testpassword@localhost:12345"
    )


@given_env_vars_via_shell_variables(mongo_is_models_repo_env_vars_sample)
def test_settings_when_source_is_mongo_db_and_variables_set_up_via_shell_variables():
    # When
    settings = Settings()

    # Then
    assert settings.version == "4.0.4"
    assert settings.environment == "test"
    assert settings.models_repository.database_name == "model-registry"
    assert settings.models_repository.source == "mongo"
    assert settings.models_repository.host == "localhost"
    assert settings.models_repository.port == 12345
    assert settings.models_repository.username == "testusername"
    assert settings.models_repository.password == "testpassword"
    assert (
        settings.models_repository.connection
        == "mongodb://testusername:testpassword@localhost:12345"
    )


# local file
@given_env_vars_via_dot_env_file(fs_is_models_repo_env_vars_sample)
def test_settings_when_source_is_file_system_and_variables_set_up_via_dot_env_file(env_path):
    # When
    settings = Settings(env_file=env_path)

    # Then
    assert settings.version == "4.0.4"
    assert settings.environment == "test"
    assert settings.models_repository.source == "fs"
    assert settings.models_repository.directory == "resources"


@given_env_vars_via_shell_variables(fs_is_models_repo_env_vars_sample)
def test_settings_when_source_is_file_system_and_variables_set_up_via_shell_variables():
    # When
    settings = Settings()

    # Then
    assert settings.version == "4.0.4"
    assert settings.environment == "test"
    assert settings.models_repository.source == "fs"
    assert settings.models_repository.directory == "resources"


@given_env_vars_via_shell_variables(
    common_env_vars, {"models_repository__source": "unknown-source"}
)
def test_settings_when_source_is_unknown_and_variables_set_up_via_shell_variables_and_expects_validation_error():
    with pytest.raises(ValidationError) as err_msg:
        Settings()

        assert "models_repository" in err_msg
