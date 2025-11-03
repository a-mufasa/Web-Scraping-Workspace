# Web Scraping Workspace

Repository for the code belonging to one-off web scraping/parsing projects. Note that some of these websites are **private**, therefore you may not be able to run the scraping/parsing for them. As such, any private data will be omitted from this repository.

Each scraper directory will contain it's own `README.md` providing the corresponding instructions.

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for Python package management. Install uv first if you haven't already.

Then install dependencies:

```
uv sync
```

Run any script with:

```
uv run python Home-Depot-Stores/scrape.py
uv run python Lowes-Stores/scrape.py
```

All Python projects in this workspace share the same dependencies defined in `pyproject.toml`.
