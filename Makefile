TEST = poetry run pytest -x -s --cov=learn_lark --durations=0 -r A tests/

pre-commit:
	poetry run pre-commit run --all-files

pre-commit-install:
	poetry run pre-commit install

pre-commit-update:
	poetry run pre-commit autoupdate

test:
	$(TEST)

test-name:
test-name:
ifdef name
	$(TEST) -k $(name)
else
	@echo Syntax is 'make $@ name=<test name>'
endif
