# Shoutout cargo-bins/cargo-quickinstall for the help command below
.PHONY: help
help: ## Display this help screen
	@grep -E '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST)  | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.venv:  ## Create a virtual environment from lockfile
	uv sync --locked --group docs

.PHONY: clean
clean:
	find ./src | grep -E "(__pycache__$$)" | xargs rm -rf
	find ./src | grep -E "(\.pyc$$)" | xargs rm -rf
	find ./src | grep -E "(\.pyo$$)" | xargs rm -rf

	rm -vrf .mypy_cache
	rm -vrf .ruff_cache

	rm -vrf dist/

.PHONY: check-format
check-format: ##  Check formatting, but do not fix
	uv run ruff format src --check

.PHONY: format
format: ##  Fix imports and formatting
	uv run ruff check --fix --select I 
	uv run ruff format src

.PHONY: types
types:  # Run the type checker
	uv run mypy src

.PHONY: lint
lint:  ## Run the linter
	uv run ruff check src

.PHONY: check  
check: format types lint  ## Run static checks (format, types, lint)

.PHONY: build-docs
build-docs:  ## Build documentation in the ./out directory
	uv run mkdocs build --site-dir out

.PHONY: serve-docs
serve-docs:  ## Serve docs on localhost:8000
	uv run mkdocs serve

.PHONY: set-version
set-version: ## Change version by passing in "v=x.y.z", updating pyproject.toml, __init__.py and lockfile
	@if [ -z "$(v)" ]; then \
        echo "Error: v is required. Usage: make set-version v=value"; \
        exit 1; \
    fi

	sed -i '' 's/^version *= *".*"/version = "$(v)"/' pyproject.toml
	sed -i '' 's/^__version__ *= *".*"/__version__ = "$(v)"/' src/mkdocs_about/__init__.py

	uv lock --upgrade-package mkdocs-about

