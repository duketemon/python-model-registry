from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import Response

from src.api.deps import create_models_repository
from src.core.logger import logger
from src.core.models_repositories.base import (
    Model,
    ModelExistsError,
    ModelNotFoundError,
    ModelsRepository,
)

app = FastAPI(title="model-registry")


@app.get("/health_check")
async def health_check() -> str:
    """health check endpoint"""

    return "I shouldn't have to die to feel alive"


@app.post("/")
async def save_model(
    name: str,
    version: str,
    file: UploadFile,
    models_repo: Annotated[ModelsRepository, Depends(create_models_repository)],
):
    """Save the model endpoint"""

    logger.info("Received the saved model request")
    input_file_extension = "mlmodel"
    if file.filename is not None:
        path = Path(file.filename)
        if path.suffix:
            input_file_extension = path.suffix[1:]

    model_content = await file.read()
    model = Model(
        name=name,
        version=version,
        content=model_content,
        file_extension=input_file_extension,
    )

    try:
        models_repo.save_model(model)
        message = f"Model {model} successfully saved"
        logger.info(message)
        return message

    except ModelExistsError as err:
        message = str(err)
        raise HTTPException(status_code=409, detail=message) from err


@app.get("/", response_class=Response)
async def get_model(
    name: str,
    version: str,
    models_repo: Annotated[ModelsRepository, Depends(create_models_repository)],
):
    """Fetch the model endpoint"""

    logger.info("Received the get model request")

    try:
        model = models_repo.get_model(name, version)
        filename = ModelsRepository.create_model_file_name(name, version, model.file_extension)
        logger.info(f"Fetched {model} model")
        return Response(
            content=model.content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except ModelNotFoundError as err:
        message = str(err)
        raise HTTPException(status_code=404, detail=message) from err


@app.delete("/")
async def delete_model(
    name: str,
    version: str,
    models_repo: Annotated[ModelsRepository, Depends(create_models_repository)],
):
    """Delete the model endpoint"""

    logger.info("Received the delete model request")

    try:
        models_repo.delete_model(name, version)
        message = f"Model {name}:{version} successfully deleted"
        logger.info(message)
        return message

    except ModelNotFoundError as err:
        message = str(err)
        raise HTTPException(status_code=404, detail=message) from err
