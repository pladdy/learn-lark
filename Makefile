pre-commit:
	poetry run pre-commit run --all-files

pre-commit-install:
	poetry run pre-commit install

pre-commit-update:
	poetry run pre-commit autoupdate

test:
	poetry run pytest -x --cov=learn_lark tests/
