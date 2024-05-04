import pytest
from pymongo.database import Collection


@pytest.fixture()
def collection_name() -> str:
    return "my-collection"


@pytest.fixture()
def collection_filter() -> dict:
    return {"age": "55", "location": "Italy"}


# save one item
def test_save_one_item(mocker, mongo_client, collection_name):
    # Given
    expected_inserted_item_id = "6B29FC40-CA47-1067-B31D-00DD010662DA"

    # When
    mocker.patch.object(Collection, "_insert_one", return_value=expected_inserted_item_id)
    actual_inserted_item_id = mongo_client.save_one_item(collection_name, {"status": 404})
    # Then
    assert actual_inserted_item_id == expected_inserted_item_id


def test_save_one_item_when_pass_non_dict_like_object_as_arg_and_expects_type_error(
    mongo_client, collection_name
):
    # Given
    document = ["status", 404]

    # Then
    with pytest.raises(TypeError):
        # When
        mongo_client.save_one_item(collection_name, document)


# delete one item
def test_delete_one_item_when_one_item_exist_and_deleted(
    mocker, mongo_client, collection_name, collection_filter
):
    # Given
    expected_deleted_count = 1
    mocked_response = {"n": expected_deleted_count}

    # When
    mocker.patch.object(Collection, "_delete_retryable", return_value=mocked_response)
    actual_deleted_count = mongo_client.delete_one_item(collection_name, collection_filter)
    # Then
    assert actual_deleted_count == expected_deleted_count


def test_delete_one_item_when_zero_item_exist_and_nothing_deleted(
    mocker, mongo_client, collection_name, collection_filter
):
    # Given
    expected_deleted_count = 0
    mocked_response = {"n": expected_deleted_count}

    # When
    mocker.patch.object(Collection, "_delete_retryable", return_value=mocked_response)
    actual_deleted_count = mongo_client.delete_one_item(collection_name, collection_filter)
    # Then
    assert actual_deleted_count == expected_deleted_count


# get one item
def test_get_one_item_when_no_items_found_as_expected(
    mocker, mongo_client, collection_name, collection_filter
):
    # Given
    mocked_cursor = get_mocked_cursor()

    # When
    mocker.patch.object(Collection, "find", return_value=mocked_cursor)
    document = mongo_client.get_one_item(collection_name, collection_filter)
    # Then
    assert document is None


def test_get_one_item_when_item_found_as_expected(
    mocker, mongo_client, collection_name, collection_filter
):
    # Given
    given_document = {"status": 200}
    mocked_cursor = get_mocked_cursor(given_document)

    # When
    mocker.patch.object(Collection, "find", return_value=mocked_cursor)
    actual_document = mongo_client.get_one_item(collection_name, collection_filter)
    # Then
    assert actual_document == given_document


def get_mocked_cursor(*items):
    class MockedCursor:
        def limit(self, *args, **kwargs):
            return items

    return MockedCursor()
