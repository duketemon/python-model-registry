# End-to-End Testing
## How to run tests?
1. Up all needed services
```commandline
make up
```

2. Run tests
```commandline
make tests
```

3. Down all launched services
```commandline
make down
```

## Setup
1. Mongo DB as the models storage
2. fastapi as a web service

## Test Cases
### Save New Model Successfully
Description: Verify that a new model can be saved successfully in the registry. Steps:  
1. Send a POST request to save a new model with valid parameters.
2. Assert that the response status code is 200 OK.
3. Verify that the registered model exists in the registry database.

### Save Model with Existing Name and Version
Description: Ensure that attempting to save a model with an existing name and version returns the appropriate error.  Steps:
1. Save a model with a specific name and version.
2. Attempt to save another model with the name and version.
3. Assert that the response status code is 409 Conflict.
4. Verify that the response body contains an appropriate error message indicating the ID is already in use.

### Fetch Existing Model Successfully
Description: Ensure that an existing model can be fetched from the registry. Steps:
1. Send a GET request to fetch an existing model by its name and version.
2. Assert that the response status code is 200 OK.
3. Verify that the fetched model's details match the expected values.

### Fetch Non-Existent Model
Description: Confirm that attempting to fetch a non-existent model returns the appropriate error. Steps:
1. Send a GET request to fetch a model that does not exist in the registry.
2. Assert that the response status code is 404 Not Found.
3. Verify that the response body contains an appropriate error message indicating the model does not exist.

### Delete Existing Model
Description: Verify that an existing model can be deleted from the registry. Steps:
1. Send a DELETE request to delete an existing model by its name and version.
2. Assert that the response status code is 200 OK.
3. Attempt to fetch the deleted model and verify that it returns a 404 Not Found error.

### Delete Non-Existent Model
Description: Confirm that attempting to delete a non-existent model returns the appropriate error. Steps:
1. Send a DELETE request to delete a model that does not exist in the registry.
2. Assert that the response status code is 404 Not Found.
3. Verify that the response body contains an appropriate error message indicating the model does not exist.


