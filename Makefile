.PHONY: install install-dev run test lint clean

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	python run.py

test:
	pytest tests/ -v

lint:
	flake8 app/
	pylint app/ --fail-under=7.0

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -f blog.db test_blog.db