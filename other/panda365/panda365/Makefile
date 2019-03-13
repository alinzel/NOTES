.PHONY: clean clean-test clean-pyc
clean: clean-test clean-pyc
ENV:=dev


clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage*
	rm -fr htmlcov
	rm -f junit.xml

install: clean
	pip install -r requirements/${ENV}.txt

lint:
	flake8

lint-changes:
	flake8 $$(git status -s | grep -E '\.py$$' | cut -c 4-)

test .coverage:
	pytest --cov-report= --cov=pd --cov-fail-under=100 --reset-db --schema-mode=alembic pd

test_sqla:
	pytest --cov-report= --cov=pd --cov-fail-under=100 --reset-db --schema-mode=sqla pd

cov: .coverage
	@coverage report --skip-covered

htmlcov: .coverage
	@coverage html --skip-covered
	@echo "open htmlcov/index.html"

htmlcov-debug: clean
	$(MAKE) htmlcov -i

hooks:
	@printf '#!/usr/bin/env sh\nmake lint-changes' > .git/hooks/pre-commit
	@printf '#!/usr/bin/env sh\nmake lint test' > .git/hooks/pre-push
	@chmod u+x .git/hooks/*
	@echo "done"

flask:  # set FLASK_APP
	@>&2 echo 'set FLASK_APP to main.py'
	@echo "export FLASK_APP=main.py"
	@echo "export FLASK_DEBUG=1"

ci junit.xml: clean lint
	$(MAKE) test PYTEST_ADDOPTS=--junit-xml=junit.xml htmlcov

TRANSLATIONS=pd/translations
DOMAIN=messages

babel-extract:
	pybabel extract -F $(TRANSLATIONS)/messages.cfg --no-location -k lazy_gettext -o $(TRANSLATIONS)/messages.pot pd

babel-init: babel-extract
	pybabel init -D $(DOMAIN) -i $(TRANSLATIONS)/messages.pot -d $(TRANSLATIONS) -l $(LANG)

babel-update: babel-extract
	pybabel update -D $(DOMAIN) -i $(TRANSLATIONS)/messages.pot --no-wrap -d $(TRANSLATIONS)
babel-compile:
	pybabel compile -D $(DOMAIN) -d $(TRANSLATIONS)
