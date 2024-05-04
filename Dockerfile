# uses the official python's image
FROM python:3.11-slim

# set up a working dir
WORKDIR /app

# prepare the docker image
RUN apt-get update -y && apt-get upgrade -y && pip install poetry

# deep copy of the whole src directory
ADD src ./src
# copy the list of dependencies
ADD pyproject.toml .
# copy the list of dependencies (compiled)
ADD poetry.lock .

# install dependencies
RUN poetry install --only main --no-root

# run the service
CMD ["poetry", "run", "uvicorn", "src.api.run:app", "--host", "0.0.0.0", "--port", "80"]
