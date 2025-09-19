.PHONY: clean build install dev-install upload test format lint setup help

help:
	@echo "Available targets:"
	@echo "  setup       - Install development dependencies"
	@echo "  clean       - Remove build artifacts"
	@echo "  build       - Build source and wheel distributions"
	@echo "  install     - Install package"
	@echo "  dev-install - Install package in development mode"
	@echo "  upload      - Upload to PyPI"
	@echo "  test        - Run tests"
	@echo "  format      - Format code with black"
	@echo "  lint        - Lint code"

setup:
	pip install -r requirements-dev.txt

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	@python -c "import build" 2>/dev/null || pip install build
	python -m build

install:
	pip install .

dev-install:
	pip install -e .

upload: build
	@python -c "import twine" 2>/dev/null || pip install twine
	python -m twine upload dist/*

test:
	python -m pytest

format:
	python -m black .

lint:
	python -m black .