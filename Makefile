.PHONY: help install install-dev test lint format clean build publish docker-build docker-run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest --cov=gitignore_gen --cov-report=term-missing

test-verbose: ## Run tests with verbose output
	pytest -v --cov=gitignore_gen --cov-report=term-missing

test-watch: ## Run tests in watch mode
	pytest-watch -- --cov=gitignore_gen

lint: ## Run linting checks
	flake8 gitignore_gen tests
	black --check gitignore_gen tests
	isort --check-only gitignore_gen tests
	mypy gitignore_gen

format: ## Format code
	black gitignore_gen tests
	isort gitignore_gen tests

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

publish: ## Publish to PyPI (requires TWINE_USERNAME and TWINE_PASSWORD)
	twine upload dist/*

docker-build: ## Build Docker image
	docker build -t gitignore-gen .

docker-run: ## Run gitignore-gen in Docker
	docker run --rm -v $(PWD):/workspace -w /workspace gitignore-gen

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

security: ## Run security checks
	bandit -r gitignore_gen
	safety check

docs: ## Generate documentation
	# Add documentation generation commands here
	@echo "Documentation generation not yet implemented"

release: ## Create a new release
	@echo "Creating new release..."
	@read -p "Enter version (e.g., 1.0.0): " version; \
	read -p "Enter release notes: " notes; \
	echo "Creating release v$$version..."; \
	git tag -a "v$$version" -m "Release v$$version: $$notes"; \
	git push origin "v$$version"

check: ## Run all checks (lint, test, security)
	make lint
	make test
	make security

dev-setup: ## Set up development environment
	make install-dev
	make pre-commit-install
	@echo "Development environment setup complete!"

ci: ## Run CI checks locally
	make lint
	make test
	make security
	make build 