# Models Registry service
## Overview
Models Registry is the service that exposes API to save, fetch and delete machine learning models. 
Currently, the service is capable to use Mongo DB and file system to manage machine learning models.  
Models registry supports the versioning feature that allows to store several versions of the same model. Model tagging feature is coming later

## Exposed endpoints
`POST / {model_name} {model_version} {file}`  
Saves `file` with the name = `model_name` and version = `model_version`

`GET / {model_name} {model_version}`  
Returns a model as a file with the name = `model_name` and version = `model_version` 

`DELETE / {model_name} {model_version}`  
Deletes from a storage the model with the name = `model_name` and versions = `model_version`

`GET /health_check`  
health check endpoint

`GET /docs`  
Swagger UI

`GET /redoc`  
Redoc UI

## Project Files Structure
`src` - source code of the models registry service  
`tests` - unit tests of the models registry service  
`tests-e2e` - end to end tests of the models registry service  

# How to contribute
Contributions are always welcomed. There is a lot of ways how you can help to the project.
* Contribute to the [unit tests](https://github.com/duketemon/python-models-registry/tree/main/tests) to make it more reliable.
* Contribute to the [end-to-end tests](https://github.com/duketemon/python-models-registry/tree/main/tests-e2e) to make it more reliable.
* Look for [issues with tag "help wanted"](https://github.com/duketemon/python-models-registry/issues?q=is%3Aissue+is%3Aopen+label%3A"help+wanted") and submit pull requests to address them.
* [Open an issue](https://github.com/duketemon/python-models-registry/issues) to report problems or recommend new features.
