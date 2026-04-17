.PHONY: install run clean

install:
	pip install -r requirements.txt

run:
	python run.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -f blog.db