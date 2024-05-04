run:
	set -a && source .env && uvicorn src.api.run:app --reload

test:
	pytest tests -vvv

fmt:
	isort .
	black .

verify:
	pylint src
	mypy src
