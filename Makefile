.PHONY: reproduce setup scan test
PYTHON ?= python3
setup:
	git config core.hooksPath .githooks
	$(PYTHON) scripts/bootstrap.py
scan:
	$(PYTHON) scripts/scan_anonymity.py
reproduce: setup scan
	.venv/bin/python scripts/reproduce.py
test: setup
	.venv/bin/python -m unittest discover -s tests -v
