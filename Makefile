help:
	@echo "register		Send pack to pipy"
	@echo "test			Run setup tests"
	@echo "install		Install packages to develop"

install:
	pip install -r requiremets.txt

test:
	python setup.py test

register:
	python setup.py register
    python setup.py build bdist_wheel bdist
    twine upload dist/*
