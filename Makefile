.PHONY: install test clean docs run-api run-dashboard docker-build docker-run validate

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v --cov=stratica

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov build dist *.egg-info .pytest_cache .mypy_cache

docs:
	cd docs && make html
	@echo "📚 Documentation available at docs/build/html/index.html"

run-api:
	stratica serve --api --port 8000 --host 0.0.0.0

run-dashboard:
	stratica serve --dashboard --port 8501 --host 0.0.0.0

docker-build:
	docker build -t stratica:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

validate:
	stratica doctor
	python scripts/validate_parameters.py --tci 96.2

lint:
	black --check stratica tests
	isort --check stratica tests
	flake8 stratica tests
	mypy stratica

format:
	black stratica tests
	isort stratica tests

.PHONY: help
help:
	@echo "📋 STRATICA Makefile Commands:"
	@echo "  make install       - Install package with dev dependencies"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make docs          - Build documentation"
	@echo "  make run-api       - Run API server"
	@echo "  make run-dashboard - Run dashboard"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker Compose"
	@echo "  make validate      - Validate installation"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
