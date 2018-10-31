.PHONY: clean clean-test clean-pyc clean-build help lint coverage coverage-html release dist install run debug docs
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"
PIPENV := pipenv
PIPRUN := $(PIPENV) run
PIPINST := $(PIPENV) --bare install --dev --skip-lock

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts
	make -C docs clean

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	$(PIPRUN) pip uninstall -y nncli

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .tox

lint: ## check style with pylint
	$(PIPRUN) pylint nncli tests --disable=parse-error
	$(PIPRUN) vulture nncli .vulture_whitelist.py

test: ## run tests quickly with the default Python
	$(PIPRUN) python -m pytest

test-all: ## run tests on every Python version with tox
	$(PIPRUN) tox

test-install: ## install dependenices from Pipfile (for tox / CI builds)
	$(PIPINST)

coverage: ## check code coverage quickly with the default Python
	$(PIPRUN) python -m pytest --cov=nncli

coverage-html: coverage ## generate an HTML report and open in browser
	$(PIPRUN) coverage html
	$(BROWSER) htmlcov/index.html

release: dist ## package and upload a release
	twine upload -s dist/*

dist: ## builds source and wheel package
	$(PIPRUN) flit build
	ls -l dist

docs: ## builds the sphinx documentation and opens in the browser
	make -C docs html
	make -C docs latexpdf
	make -C docs man
	$(BROWSER) docs/build/html/index.html

install: ## install the package to the active Python's site-packages
	$(PIPRUN) flit install --deps=none

run: ## run the package from site-packages
	$(PIPRUN) python -m nncli $(cmd)

debug: install ## debug the package from site packages
	$(PIPRUN) pudb3 $$($(PIPRUN) which nncli) $(cmd)
