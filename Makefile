.PHONY: help install test run demo clean

help: ## Show this help message
	@echo "Donizo Material Scraper - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-mock pytest-cov

test: ## Run tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=scraper --cov-report=html

run: ## Run the scraper
	python3 scraper.py

demo: ## Run the demo
	python3 demo.py

api: ## Start the API server
	python3 api_server.py

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ htmlcov/

lint: ## Run linting (if flake8 is installed)
	flake8 *.py config/ tests/ || echo "flake8 not installed, skipping linting"

format: ## Format code (if black is installed)
	black *.py config/ tests/ || echo "black not installed, skipping formatting"

all: install test run ## Install, test, and run
