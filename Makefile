install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv --cov=rex_pool_reservations tests/

lint:
	pylint --disable=R,C,W0511 rex_pool_reservations.py

all: install lint test