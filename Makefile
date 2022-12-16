pre-commit:
	poetry run pre-commit run --all-files

pre-commit-install:
	poetry run pre-commit install

pre-commit-update:
	poetry run pre-commit update

test:
	poetry run pytest --cov=learn_lark tests/
