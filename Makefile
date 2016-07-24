# Makefile


.PHONY: pep8
pep8:
	python setup.py pep8


.PHONY: lint
lint: pep8


# EOF
