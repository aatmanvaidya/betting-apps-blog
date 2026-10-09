# AGENTS.md

Instructions for AI coding agents working in this project (maannganet).

## Python

- Use `uv` for anything Python-related: running scripts, managing the environment, and managing dependencies. Do not use bare `pip`, `python -m venv`, or `poetry`.
- Activate the environment by sourcing the `.venv/` folder from the project root before running Python:
  ```sh
  source .venv/bin/activate
  ```
- Run Python with `uv run python`, for example:
  ```sh
  uv run python path/to/script.py
  ```
- To add or install any Python library, always use `uv add <package>`. Never use `pip install` or edit `pyproject.toml` dependencies by hand.
