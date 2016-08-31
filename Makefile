# Makefile


python_package := apiramid
pylint_packages := setup.py $(python_package) tests/*.py


# join with commas
comma := ,
empty :=
space := $(empty) $(empty)
joinwithcommas = $(subst $(space),$(comma),$(wildcard $(1)))


.PHONY: pep8
pep8:
	python setup.py pep8


.PHONY: pylint
pylint:
	python setup.py --quiet lint --lint-reports=no \
		--lint-packages=$(call joinwithcommas,$(pylint_packages))


.PHONY: lint
lint: pep8 pylint


# EOF
